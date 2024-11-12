import streamlit as st
import csv
from io import StringIO

st.title("Flow Log Tagging Application")
flow_log_file = st.file_uploader("Upload Flow Log File", type=["txt"])
lookup_table_file = st.file_uploader("Upload Lookup Table", type=["txt"])

def parse_lookup_table(file_content):
    lookup_dict = {}
    file = file_content.getvalue().decode("utf-8")
    reader = csv.reader(file, delimiter=',')
    next(reader) 
    for row in reader:
        dstport = row[0].strip()
        tag = row[2].strip()
        lookup_dict[dstport] = tag
    return lookup_dict

def parse_flow_logs(file, lookup_dict):
    flow_logs = []
    for line in file:
        fields = line.split()
        
        if len(fields) < 6:
            print(f"Skipping invalid line due to insufficient fields: {line}")
            continue

        dstport = fields[5]

        tag = lookup_dict.get(dstport, "Untagged")

        flow_logs.append({
            "dstport": dstport,
            "raw_data": line.strip(),
            "tag": tag
        })

    return flow_logs

def map_tags(flow_logs):
    tag_counts = {}
    dstport_counts = {}

    for flow_log in flow_logs:
        tag = flow_log["tag"]
        dstport = flow_log["dstport"]

        # Count tags
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

        # Count dstport occurrences
        dstport_counts[dstport] = dstport_counts.get(dstport, 0) + 1

    return tag_counts, dstport_counts

def generate_csv(data, headers):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in data:
        writer.writerow(row.values())
    output.seek(0)
    return output.getvalue()

if flow_log_file and lookup_table_file:
    lookup_dict = parse_lookup_table(lookup_table_file)
    flow_logs = parse_flow_logs(flow_log_file, lookup_dict)
    tag_counts, port_protocol_counts = map_tags(flow_logs)
    
    st.write("### Flow Logs")
    st.write(flow_logs)
    st.write("### Lookup Table")
    st.write(lookup_dict)

    st.write("### Tag Counts")
    tag_counts_display = [{"Tag": k, "Count": v} for k, v in tag_counts.items()]
    st.write(tag_counts_display)

    st.write("### Port/Protocol Combination Counts")
    port_protocol_counts_display = [
        {"Port": k[0], "Protocol": k[1], "Count": v} 
        for k, v in port_protocol_counts.items()
    ]
    st.write(port_protocol_counts_display)

    st.download_button("Download Tag Counts",
                       data=generate_csv(tag_counts_display, ["Tag", "Count"]),
                       file_name="tag_counts.csv", mime="text/csv")

    st.download_button("Download Port/Protocol Counts",
                       data=generate_csv(port_protocol_counts_display, ["Port", "Protocol", "Count"]),
                       file_name="port_protocol_counts.csv", mime="text/csv")
else:
    st.error("Please upload both files")
