import paperinquirer

resource_dirs = "path/to/pdf/files"
question = "A/question/to/ask"

inquirer = paperinquirer.PaperInquirer(resource_dirs=resource_dirs)
print(inquirer.inquire(question))