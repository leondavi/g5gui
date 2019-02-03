


class ParserCore:
    def __init__(self,file_path):
        self.file_path

    def parse(self):
        with open(self.file_path) as f:
            lines = f.readlines()
        lines = [x.strip() for x in lines]

        for line in lines:
            words = line.split(' ')
            for idx,word in enumerate(words):




