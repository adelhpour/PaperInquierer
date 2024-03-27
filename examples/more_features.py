import paperinquirer

resource_dirs = "path/to/resource_dirs"
storage_dir = "path/to/storage"
question = "A/question/to/ask"

inquirer = paperinquirer.PaperInquirer(resource_dirs, storage_dir)
print(inquirer.inquire(question))
