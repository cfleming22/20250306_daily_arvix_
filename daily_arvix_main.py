import sys
import time
import pytz
from datetime import datetime, timedelta

from utils import (
    get_daily_papers_by_keyword_with_retries,
    generate_table,
    back_up_files,
    restore_files,
    remove_backups,
    get_daily_date
)

# Set timezone to Los Angeles
la_timezone = pytz.timezone('America/Los_Angeles')

# Define start and end dates
start_date = datetime(2022, 10, 3, tzinfo=la_timezone)
end_date = datetime(2025, 3, 6, tzinfo=la_timezone)

#Define categories

categories = [
    "Artificial Intelligence", "Computation and Language", "Computation Complexity",
    "Computation Engineering, Finance and Science", "Computational Geometry",
    "Computer Science and Game Theory", "Computer Vision and Pattern Recognition",
    "Computers and Society", "Cryptography and Security", "Data Structures and Algorithms",
    "Databases", "Digital Libraries", "Discrete Mathematics",
    "Distributed, Parallel, and Cluster Computing", "Emerging Technologies",
    "Formal Languages and Automata Theory", "General Literature", "Graphics",
    "Hardware Architecture", "Human-Computer Interaction", "Information Retrieval",
    "Information Theory", "Logic in Computer Science", "Machine Learning",
    "Mathematical Software", "Multiagent Systems", "Multimedia",
    "Networking and Internet Architecture", "Neural and Evolutionary Computing",
    "Numerical Analysis", "Operating System", "Other Computer Science",
    "Performance", "Programming Languages", "Robotics",
    "Social and Information Networks", "Software Engineering", "Sound",
    "Symbolic Computation", "Systems and Control"
]

# Define Query Limits
max_result = 100  # Maximum query results per category
issues_result = 15  # Maximum papers included in the issue

# Define Column Names 
column_names = ["Title", "Authors", "Abstract", "Link", "Tags", "Comment", "Date"]

# Writing Initial Content to README.md 
current_date = datetime.now(la_timezone).strftime("%Y-%m-%d")

back_up_files()  # Backup existing files

f_rm = open("README.md", "w")
f_rm.write("# Daily Papers\n")
f_rm.write("The project automatically fetches the latest papers from arXiv based on keywords.\n\n")
f_rm.write("The subheadings in the README file represent the search keywords.\n\n")
f_rm.write("Only the most recent articles for each keyword are retained, up to a maximum of {0} papers.\n\n".format(max_result))
f_rm.write("You can click the 'Watch' button to receive daily email notifications.\n\n")
f_rm.write("Last update: {0}\n\n".format(current_date))


# Prepare Issue Template

f_is = open(".github/ISSUE_TEMPLATE.md", "w")
f_is.write("---\n")
f_is.write("title: Latest {0} Papers - {1}\n".format(issues_result, get_daily_date()))
f_is.write("labels: documentation\n")
f_is.write("---\n")
f_is.write("# Latest {0} Papers - {1}\n".format(issues_result, get_daily_date()))
f_is.write("\n")

for category in categories:
    print("Processing category: {0}".format(category))
    table = generate_table(get_daily_papers_by_keyword_with_retries(category, max_result), column_names, issues_result)
    f = open(category + ".md", "w")
    f.write(table)
    f.close()   
    time.sleep(3)  # Sleep for 3 seconds to avoid rate limiting

remove_backups()  # Remove backup files

# Main Loop
current_date_iter = start_date

while current_date_iter <= end_date:
    formatted_date = current_date_iter.strftime("%Y-%m-%d")
    print(f"Fetching papers for date: {formatted_date}")

    for keyword in categories:
        f_rm.write("## {0} ({1})\n".format(keyword, formatted_date))
        f_is.write("## {0} ({1})\n".format(keyword, formatted_date))

        if len(keyword.split()) == 1:
            link = "AND"
        else:
            link = "OR"

        papers = get_daily_papers_by_keyword_with_retries(keyword, column_names, max_result, link)

        ### ✅ **Step 6d: Error Handling (Unchanged)**
        if papers is None:
            print(f"Failed to get papers for {keyword} on {formatted_date}")
            f_rm.close()
            f_is.close()
            restore_files()
            sys.exit("Failed to get papers!")

        ### ✅ **Step 7: Writing Results to README and Issue Files (Unchanged)**
        rm_table = generate_table(papers)
        is_table = generate_table(papers[:issues_result], ignore_keys=["Abstract"])

        f_rm.write(rm_table)
        f_rm.write("\n\n")
        f_is.write(is_table)
        f_is.write("\n\n")

        ### ✅ **Step 8: Delay Between Requests (Unchanged)**
        time.sleep(3)

    # Increment date by one day
    current_date_iter += timedelta(days=1)
    # Closing Files and Cleanup
    f_rm.close()
    f_is.close()
    remove_backups()
    print("Scraping completed successfully!")

