from typing import List

from field.field import Field

FieldMatrix = List[List[Field.Cell]]


# По сути читает и записывает матрицу поля в бинарном виде
class SaveFileHandler:
    @staticmethod
    def open_file(file: str) -> FieldMatrix:
        with open(file, 'rb') as f:
            buffer = f.read().split('\n'.encode())

        buffer = [[Field.Cell(pos_x=x, pos_y=y, state=int(state))
                   for x, state in enumerate(list(line.decode()))] for y, line in enumerate(buffer)]
        return buffer

    @staticmethod
    def save_file(file: str, content: FieldMatrix) -> None:
        with open(file, 'wb') as f:
            for i, line in enumerate(content):
                s = ''.join(str(c.get_state()) for c in line)
                if i != len(content) - 1:
                    s += '\n'
                f.write(s.encode())
