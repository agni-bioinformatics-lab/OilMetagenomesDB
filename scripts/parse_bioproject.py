"""Collect the metadata of one NCBI BioProject and pre-fill draft rows for the
OilMetagenomesDB tables.

Usage:
    python scripts/parse_bioproject.py -id PRJNA729662
    python scripts/parse_bioproject.py -id PRJNA729662 --project-name Author2021 \
        --year 2021 --doi 10.1000/example -o new_study/

Writes three TSV files to the output directory (default: current directory):
    <id>_raw.tsv        everything NCBI reports about every run and its BioSample
    <id>_libraries.tsv  draft rows for common_libraries.tsv (one row per run)
    <id>_samples.tsv    draft rows for common_samples.tsv (one row per SRS sample)

Only the Python standard library is needed. NCBI allows 3 requests per second
without an API key; set NCBI_API_KEY in the environment to raise this to 10.

The drafts contain only what NCBI knows. Fields that must come from the article
(physico-chemical parameters, study focus, library preparation details, ...) are
left empty in the samples draft and set to "unknown" in the libraries draft, as in
the existing rows. Fill them in and validate against the JSON schemas before
adding anything to the real tables; the script reports what still needs attention.
"""
import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
SDL = "https://locate.ncbi.nlm.nih.gov/sdl/2/retrieve"
BATCH = 100
SCHEMAS_DIR = Path(__file__).resolve().parent.parent

SAMPLE_COLUMNS = [
    "project_name", "publication_year", "publication_doi", "oil_reservoir", "oil_wells",
    "latitude", "longitude", "geo_loc_name", "study_primary_focus", "study_process",
    "depth", "temp", "pH", "salinity", "API", "NO3-", "PO43-", "SO42-", "Ca2+", "Mg2+",
    "Na+", "K+", "Cl-", "HCO3-", "acetate", "sample_name", "feature", "material",
    "collection_date", "archive", "archive_project", "archive_accession",
]
LIBRARY_COLUMNS = [
    "project_name", "publication_year", "publication_doi", "sample_name", "archive",
    "archive_project", "archive_accession", "library_name", "strand_type",
    "library_polymerase", "library_treatment", "library_concentration", "PCR_cycle_count",
    "instrument_model", "library_layout", "library_strategy", "amplicon_variable_region",
    "read_count", "archive_data_accession", "download_links", "download_md5s",
    "download_sizes",
]

_last_request = 0.0


def fetch(url, params=None):
    """GET with rate limiting and a few retries; returns the body as text."""
    global _last_request
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    gap = 0.11 if os.environ.get("NCBI_API_KEY") else 0.35
    for attempt in range(4):
        time.sleep(max(0.0, _last_request + gap - time.time()))
        _last_request = time.time()
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return resp.read().decode("utf-8")
        except (urllib.error.URLError, TimeoutError) as err:
            if attempt == 3:
                sys.exit(f"Request failed after 4 attempts: {url}\n  {err}")
            time.sleep(2 * (attempt + 1))


def eutils(tool, **params):
    key = os.environ.get("NCBI_API_KEY")
    if key:
        params["api_key"] = key
    return fetch(EUTILS + tool + ".fcgi", params)


def batches(items, size=BATCH):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def get_runinfo(bioproject):
    """SRA runinfo rows (list of dicts) for all runs of the BioProject."""
    found = ET.fromstring(eutils(
        "esearch", db="sra", term=f"{bioproject}[BioProject]", retmax=100000))
    ids = [e.text for e in found.findall("./IdList/Id")]
    if not ids:
        sys.exit(f"No SRA records found for {bioproject}. Check the accession; "
                 "the data may be deposited in another archive or not yet public.")
    rows = []
    for chunk in batches(ids):
        text = eutils("efetch", db="sra", id=",".join(chunk), rettype="runinfo", retmode="text")
        rows += [r for r in csv.DictReader(io.StringIO(text)) if r.get("Run")]
    # the same run can be returned by several experiment records
    unique = {r["Run"]: r for r in rows}
    return sorted(unique.values(), key=lambda r: r["Run"])


def get_biosamples(accessions):
    """{SAMN accession: {attribute name: value}} from the BioSample database."""
    result = {}
    for chunk in batches(sorted(accessions)):
        root = ET.fromstring(eutils("efetch", db="biosample", id=",".join(chunk), retmode="xml"))
        for bs in root.findall("BioSample"):
            attrs = {"title": (bs.findtext("./Description/Title") or "").strip(),
                     "organism": (bs.findtext("./Description/Organism/OrganismName") or "").strip(),
                     "package": (bs.findtext("./Package") or "").strip()}
            for a in bs.findall("./Attributes/Attribute"):
                name = a.get("harmonized_name") or a.get("attribute_name")
                attrs[name] = (a.text or "").strip()
            result[bs.get("accession")] = attrs
    return result


def get_sra_files(runs):
    """{run: {"link", "md5", "size"}} of the original SRA file, from NCBI SDL."""
    result = {}
    for chunk in batches(sorted(runs), 50):
        data = json.loads(fetch(SDL, {"acc": ",".join(chunk), "accept-alternate-locations": "yes"}))
        for bundle in data.get("result", []):
            for f in bundle.get("files", []):
                if f.get("type") != "sra" or f.get("name", "").endswith(".lite"):
                    continue
                links = [loc["link"] for loc in f.get("locations", [])
                         if loc.get("link") and not loc.get("payRequired")]
                if links:
                    result[bundle["bundle"]] = {
                        "link": links[0], "md5": f.get("md5", ""), "size": str(f.get("size", ""))}
                    break
    return result


def parse_lat_lon(value):
    """'37.74 N 119.17 E' -> ('37.74', '119.17'); anything else -> ('', '')."""
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([NS])\s+(\d+(?:\.\d+)?)\s*([EW])\s*$", value or "")
    if not m:
        return "", ""
    lat = ("-" if m.group(2) == "S" else "") + m.group(1)
    lon = ("-" if m.group(4) == "W" else "") + m.group(3)
    # the schemas require a decimal point
    return (lat if "." in lat else lat + ".0"), (lon if "." in lon else lon + ".0")


def library_strategy(run):
    strategy, source = run["LibraryStrategy"].upper(), run["LibrarySource"].upper()
    if strategy == "AMPLICON":
        return "amplicon"
    if strategy == "WGS":
        return "wgs"
    if strategy == "RNA-SEQ":
        return "metatranscriptomic" if source == "METATRANSCRIPTOMIC" else "rna-seq"
    return "unknown"


def build_libraries(runs, files, args):
    rows = []
    for r in runs:
        f = files.get(r["Run"], {})
        strategy = library_strategy(r)
        rows.append({
            "project_name": args.project_name, "publication_year": args.year,
            "publication_doi": args.doi, "sample_name": r["SampleName"], "archive": "SRA",
            "archive_project": r["BioProject"], "archive_accession": r["Sample"],
            "library_name": r["LibraryName"] or r["SampleName"], "strand_type": "unknown",
            "library_polymerase": "unknown", "library_treatment": "unknown",
            "library_concentration": "unknown", "PCR_cycle_count": "unknown",
            "instrument_model": r["Model"].lower(), "library_layout": r["LibraryLayout"].lower(),
            "library_strategy": strategy,
            "amplicon_variable_region": "unknown" if strategy == "amplicon" else "None",
            "read_count": r["spots"], "archive_data_accession": r["Run"],
            "download_links": f.get("link", ""), "download_md5s": f.get("md5", ""),
            "download_sizes": f.get("size", ""),
        })
    return rows


def build_samples(runs, biosamples, args):
    rows, seen = [], set()
    for r in runs:
        if r["Sample"] in seen:
            continue
        seen.add(r["Sample"])
        bs = biosamples.get(r["BioSample"], {})
        lat, lon = parse_lat_lon(bs.get("lat_lon"))
        country = (bs.get("geo_loc_name") or "").split(":")[0].strip()
        year = re.match(r"^(\d{4})", bs.get("collection_date") or "")
        row = {c: "" for c in SAMPLE_COLUMNS}
        row.update({
            "project_name": args.project_name, "publication_year": args.year,
            "publication_doi": args.doi, "latitude": lat, "longitude": lon,
            "geo_loc_name": country, "sample_name": r["SampleName"],
            "collection_date": year.group(1) if year else "", "archive": "SRA",
            "archive_project": r["BioProject"], "archive_accession": r["Sample"],
        })
        rows.append(row)
    return rows


def load_schema(directory, column):
    path = directory / f"{column}.json"
    return json.loads(path.read_text()) if path.exists() else None


def check_rows(rows, columns, schemas_dir, label):
    """Print which values still need work. Returns the number of problems."""
    problems = {}
    for column in columns:
        schema = load_schema(schemas_dir, column) if schemas_dir.is_dir() else None
        for i, row in enumerate(rows, start=1):
            value = row[column]
            if value == "":
                kind = "empty (fill in)"
            elif schema and "enum" in schema and value not in schema["enum"]:
                kind = f"not in allowed values, e.g. {value!r}"
            elif schema and "pattern" in schema and not re.search(schema["pattern"], value):
                kind = f"does not match the pattern, e.g. {value!r}"
            else:
                continue
            problems.setdefault((column, kind), []).append(i)
    for (column, kind), idx in sorted(problems.items()):
        print(f"  [{label}] {column}: {kind} in {len(idx)} of {len(rows)} rows")
    return sum(len(v) for v in problems.values())


def write_tsv(path, rows, columns):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("-id", "--bioproject", required=True, help="BioProject accession, e.g. PRJNA729662")
    parser.add_argument("--project-name", default="", help="project_name in AuthorYear format")
    parser.add_argument("--year", default="", help="publication year")
    parser.add_argument("--doi", default="", help="DOI of the article")
    parser.add_argument("-o", "--output-dir", default=".", help="where to write the TSV files")
    parser.add_argument("--schemas-dir", default=str(SCHEMAS_DIR), help="repository root with schemas_samples/ and schemas_libraries/")
    args = parser.parse_args()
    if not re.match(r"^PRJ(NA|EB|DB)\d+$", args.bioproject):
        sys.exit("Expected a BioProject accession like PRJNA729662.")

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    schemas = Path(args.schemas_dir)

    print(f"Fetching SRA runs of {args.bioproject} ...")
    runs = get_runinfo(args.bioproject)
    print(f"  {len(runs)} runs, {len({r['Sample'] for r in runs})} samples")
    print("Fetching BioSample attributes ...")
    biosamples = get_biosamples({r["BioSample"] for r in runs if r["BioSample"]})
    print("Fetching file links, MD5 sums and sizes ...")
    files = get_sra_files([r["Run"] for r in runs])

    # raw table: runinfo columns + all BioSample attributes
    attr_names = sorted({k for a in biosamples.values() for k in a})
    raw_columns = list(runs[0].keys()) + [f"biosample:{a}" for a in attr_names] + [
        "sdl:link", "sdl:md5", "sdl:size"]
    raw = []
    for r in runs:
        row = dict(r)
        for name, value in biosamples.get(r["BioSample"], {}).items():
            row[f"biosample:{name}"] = value
        f = files.get(r["Run"], {})
        row.update({"sdl:link": f.get("link", ""), "sdl:md5": f.get("md5", ""), "sdl:size": f.get("size", "")})
        raw.append(row)

    libraries = build_libraries(runs, files, args)
    samples = build_samples(runs, biosamples, args)
    write_tsv(out / f"{args.bioproject}_raw.tsv", raw, raw_columns)
    write_tsv(out / f"{args.bioproject}_libraries.tsv", libraries, LIBRARY_COLUMNS)
    write_tsv(out / f"{args.bioproject}_samples.tsv", samples, SAMPLE_COLUMNS)
    print(f"\nWritten to {out}/: {args.bioproject}_raw.tsv, _libraries.tsv ({len(libraries)} rows), _samples.tsv ({len(samples)} rows)")

    print("\nStill to do before these rows can be added:")
    n = check_rows(libraries, LIBRARY_COLUMNS, schemas / "schemas_libraries", "libraries")
    n += check_rows(samples, SAMPLE_COLUMNS, schemas / "schemas_samples", "samples")
    if not n:
        print("  nothing found by the automatic checks")


if __name__ == "__main__":
    main()
