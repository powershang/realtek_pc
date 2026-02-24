import subprocess
import sys

# Check if the filename argument is provided
if len(sys.argv) < 2:
    print("Usage: python proj_data.py <list_filename.txt>")
    sys.exit(1)

list_filename = sys.argv[1]

# Read the list of codes from the provided file
with open(list_filename, 'r') as f:
    codes = [line.strip() for line in f if line.strip()]

output_lines = []

for code in codes:
    svn_url = f"http://cadinfo/svn/MM/{code}"
    try:
        # Run svn info and capture the output
        result = subprocess.run(['svn', 'info', svn_url], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Parse the Last Changed Date
            for line in result.stdout.splitlines():
                if line.startswith('Last Changed Date:'):
                    date = line.split('Last Changed Date:')[1].strip()
                    output_lines.append(f"{code}: {date}")
                    break
            else:
                output_lines.append(f"{code}: Last Changed Date not found")
        else:
            output_lines.append(f"{code}: svn info failed")
    except Exception as e:
        output_lines.append(f"{code}: Error - {e}")

# Write the results to a file
with open('svn_dates.txt', 'w') as f:
    for line in output_lines:
        f.write(line + '\n')

print("Done! Results have been written to svn_dates.txt")
