import subprocess

with open('ccs.txt', 'r', encoding='utf8') as f:
    ccs = f.read().strip().split('\n')

start_range = 0
end_range = 1000
sequence = 8

for cc in ccs:
    cc_num, month, year = cc.split('|')

    command = [
        "python", "bot.py",
        "--cc", cc_num.strip(),
        "--month", month.strip(),
        "--year", year.strip(),
        "--start_range", str(start_range),
        "--end_range", str(end_range),
        "--sequence", str(sequence)
    ]

    subprocess.run(command)