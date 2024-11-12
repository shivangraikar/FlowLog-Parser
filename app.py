import streamlit as st
import csv
from io import StringIO

st.title("Flow Log Tagging Application")
flow_log_file = st.file_uploader("Upload Flow Log File", type=["txt"])
lookup_table_file = st.file_uploader("Upload Lookup Table", type=["txt"])

def parse_lookup_table(file):
    lookup_dict = {}
    file_content = file.getvalue().decode("utf-8")
    reader = csv.reader(file_content.splitlines(), delimiter=',')
    next(reader)
    for row in reader:
        port, protocol, tag = row[0].strip(), row[1].strip().lower(), row[2].strip()
        key = (port, protocol)
        if key not in lookup_dict:
            lookup_dict[key] = []
        lookup_dict[key].append(tag.lower())
    return lookup_dict

def parse_flow_logs(file):
    flow_logs = []
    for line in file:
        parts = line.strip().split()
        if len(parts) > 5:
            flow_logs.append({
                "dstport": parts[5],
                "protocol": "tcp" if parts[6].lower() == "6" else "udp",
                "raw_data": line.strip()
            })
    return flow_logs


def map_tags(flow_logs, lookup_dict):
    tag_counts = {}
    port_protocol_counts = {}

    for log in flow_logs:
        key = (log['dstport'], log['protocol'].lower())
        tags = lookup_dict.get(key, ["Untagged"])
        for tag in tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        port_protocol_counts[key] = port_protocol_counts.get(key, 0) + 1

    return tag_counts, port_protocol_counts

def generate_csv(data):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(data[0].keys())
    for row in data:
        writer.writerow(row.values())
    output.seek(0)
    return output.getvalue()


if flow_log_file and lookup_table_file:
    lookup_dict = parse_lookup_table(lookup_table_file)
    flow_logs = parse_flow_logs(flow_log_file)
    tag_counts, port_protocol_counts = map_tags(flow_logs, lookup_dict)
    st.write("### Flow Logs")
    st.write(flow_logs)
    st.write("### Lookup Table")
    st.write(lookup_dict)

    st.write("### Tag Counts")
    st.write([{"Tag": k, "Count": v} for k, v in tag_counts.items()])

    st.write("### Port/Protocol Combination Counts")
    st.write([{"Port": k[0], "Protocol": k[1], "Count": v} for k, v in port_protocol_counts.items()])

    st.download_button("Download Tag Counts",
                   data=generate_csv([{"Tag": k, "Count": v} for k, v in tag_counts.items()]),
                   file_name="tag_counts.csv", mime="text/csv")

    st.download_button("Download Port/Protocol Counts",
                   data=generate_csv([{"Port": k[0], "Protocol": k[1], "Count": v} for k, v in port_protocol_counts.items()]),
                   file_name="port_protocol_counts.csv", mime="text/csv")

else:
    st.error("Please upload both files")

