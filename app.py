import csv
from collections import defaultdict
import streamlit as st
import pandas as pd
import io
import time
from io import StringIO


tag_lookup = {}
protocol_map = {}
tag_counts = defaultdict(int)
port_protocol_counts = defaultdict(int)


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

def load_lookup_table(file):
    global tag_lookup
    tag_lookup.clear()
    
    for line in io.TextIOWrapper(file):
        if line.startswith("Port,Protocol,Tag"):
            continue

        parts = line.strip().split(",")
        if len(parts) >= 3:
            port = parts[0].strip()
            protocol = parts[1].strip().lower()
            tag = parts[2].strip()
            lookup_key = f"{port}_{protocol}"
            tag_lookup[lookup_key] = tag
        else:
            st.warning(f"Skipping malformed line in lookup table: {line.strip()}")

def parseFlowLogs(file):
    global tag_counts, port_protocol_counts
    tag_counts.clear()
    port_protocol_counts.clear()
    
    for line in io.TextIOWrapper(file):
        fields = line.split()
        if len(fields) < 8:
            st.warning(f"Skipping line due to unexpected format: {line.strip()}")
            continue

        dst_port = fields[5]
        protocol_number = fields[7]
        
        protocol_name = protocol_map.get(protocol_number, "unknown").lower()
        
        lookup_key = f"{dst_port}_{protocol_name}"
        
        # Retrieve tag from tag_lookup
        tag = tag_lookup.get(lookup_key, "Untagged")

        # Update counts
        tag_counts[tag] += 1
        port_protocol_counts[(dst_port, protocol_name)] += 1


def main():
    st.title("Flow Log Parser")
    st.markdown("""
    **Steps to use:**
    - First: Upload the Lookup Table CSV
    - Second: Upload the Protocol Table CSV
    - Third: Upload the Flow Logs Text File
    - Finally: Download the Combined: Tag Counts and Port/Protocol Counts""")

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
                parseFlowLogs(log_file)
                st.success("Flow Logs Parsed")
                
                with st.spinner('Wait for it...'):
                    time.sleep(3)
                st.success("Done!")

                # Display tag counts
                st.subheader("Tag Counts")
                tag_counts_df = pd.DataFrame(tag_counts.items(), columns=["Tag", "Count"])
                st.table(tag_counts_df)
                
                # Display port/protocol combination counts
                st.subheader("Protocol/Port Counts")
                port_protocol_counts_df = pd.DataFrame(
                    [(port, protocol, count) for (port, protocol), count in port_protocol_counts.items()],
                    columns=["Port", "Protocol", "Count"]
                )
                st.table(port_protocol_counts_df)
            
                csv_buffer = StringIO()

                csv_buffer.write("Tag Counts\n")
                tag_counts_df.to_csv(csv_buffer, index=False)
                csv_buffer.write("\nPort/Protocol Counts\n")
                port_protocol_counts_df.to_csv(csv_buffer, index=False)

                csv_data = csv_buffer.getvalue()

                st.download_button(
                    label="Download Combined CSV",
                    data=csv_data,
                    file_name="output_counts.csv",
                    mime="text/csv"
                )
    

if __name__ == "__main__":
    main()