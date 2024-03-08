import paperinquirer

pdf_dir = "path/to/pdf/files"
question = "A/question/to/ask"

inquirer = paperinquirer.PaperInquirer(pdf_dir)
print(inquirer.inquire(question))