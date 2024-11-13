# Flow Log Parser

## Goal

This program is designed to parse and analyze flow logs to generate counts of tags and port+protocol combinations. It runs locally with minimal dependencies, avoiding complex packages for easier setup.

## Input Files

1. **Lookup Table (CSV)**: Maps destination port, protocol, and associated tags.
2. **Protocol Numbers (CSV)**: List of protocol numbers to extend beyond standard cases.
3. **Flow Logs**: Logs containing destination ports and protocol numbers.

## Output

A single CSV file with two sections:
- **Tag Counts**: Counts of each tag based on flow logs.
- **Port+Protocol Counts**: Counts of each unique port and protocol combination.

## Assumptions and Tests

- **Flow Logs**: Includes 40 sample logs with support for multiple protocols (ICMP, UDP, and TCP).
- **Minimal Dependencies**: Only `pandas` is used for CSV file generation.

## Usage

1. Check:[ HostApp](https://shivangraikar-flowlog-parser-app-cdeeko.streamlit.app/)
2. Download the repository, install streamlit and then 'streamlit run app.py'
