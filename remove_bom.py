input_file = "data.json"
output_file = "data_clean.json"

with open(input_file, "r", encoding="utf-16") as f:
    data = f.read()

with open(output_file, "w", encoding="utf-8") as f:
    f.write(data)

print(f"Converted UTF-16 LE file to UTF-8 and saved as {output_file}")
# with open("data.json", "rb") as f:
#     first_bytes = f.read(20)
# print(first_bytes.hex())