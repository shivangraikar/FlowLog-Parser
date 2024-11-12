import csv
from collections import defaultdict
import streamlit as st
import pandas as pd
import io

tag_lookup = {}
protocol_map = {}
tag_counts = defaultdict(int)
port_protocol_counts = defaultdict(int)

def load_lookup_table(file):
    global tag_lookup
    tag_lookup.clear()
    reader = csv.reader(io.TextIOWrapper(file))
    next(reader)
    for row in reader:
        port, protocol, tag = row[0].strip(), row[1].strip().lower(), row[2].strip()
        tag_lookup[f"{port}_{protocol}"] = tag

def load_protocol_table(file):
    global protocol_map
    protocol_map.clear()
    reader = csv.reader(io.TextIOWrapper(file))
    next(reader)
    for row in reader:
        try:
            decimal = row[0].strip()
            protocol_name = row[1].strip() if 0 <= int(decimal) <= 145 else "unknown"
            protocol_map[decimal] = protocol_name
        except ValueError:
            protocol_map[decimal] = "unknown"

# Parse the log file
def parse_flow_logs(file):
    global tag_counts, port_protocol_counts
    tag_counts.clear()
    port_protocol_counts.clear()

    for line in file:
        fields = line.split()
        if len(fields) < 8:
            continue
        
        dst_port = fields[5]
        protocol_number = fields[7]
        protocol_name = protocol_map.get(protocol_number, "unknown")
        
        # Get the tag
        lookup_key = f"{dst_port}_{protocol_name}"
        tag = tag_lookup.get(lookup_key, "Untagged")
        
        # Increment the counts
        tag_counts[tag] += 1
        port_protocol_counts[(dst_port, protocol_name)] += 1


def main():
    st.title("Flow Log Parser and Tag Counter")
    
    # Upload the lookup table
    lookup_file = st.file_uploader("Upload Lookup Table CSV", type="csv")
    if lookup_file:
        load_lookup_table(lookup_file)
        st.success("Lookup Table Loaded")
    
    # Upload the protocol table
    protocol_file = st.file_uploader("Upload Protocol Table CSV", type="csv")
    if protocol_file:
        load_protocol_table(protocol_file)
        st.success("Protocol Table Loaded")
    
    # Upload the flow logs
    log_file = st.file_uploader("Upload Flow Logs Text File", type="txt")
    if log_file:
        parse_flow_logs(log_file)
        st.success("Flow Logs Parsed")
        
        # Display tag counts
        st.subheader("Tag Counts")
        tag_counts_df = pd.DataFrame(tag_counts.items(), columns=["Tag", "Count"])
        st.table(tag_counts_df)
        
        # Display port/protocol combination counts
        st.subheader("Port/Protocol Combination Counts")
        port_protocol_counts_df = pd.DataFrame(
            [(port, protocol, count) for (port, protocol), count in port_protocol_counts.items()],
            columns=["Port", "Protocol", "Count"]
        )
        st.table(port_protocol_counts_df)

if __name__ == "__main__":
    main()
