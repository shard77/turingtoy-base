from typing import (
    Dict,
    List,
    Optional,
    Tuple,
)

import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


class TMachine:
    initial: Dict
    history: Dict
    table: Dict
    band: str
    position: int
    state: str

    def __init__(self, machine, band) -> None:
        self.initial = machine
        self.table = machine["table"]
        self.band = list(band)
        self.position = 0
        self.state = machine["start state"]
        self.history = []

    def read(self) -> str:
        return self.band[self.position]

    def write(self, val) -> None:
        self.band[self.position] = val

    def get_instruction(self) -> any:
        if self.state == "done":
            return {}

        if self.read() in self.table[self.state]:
            return self.table[self.state][self.read()]
        elif self.initial["blank"] in self.table[self.state]:
            return self.table[self.state][self.initial["blank"]]
        else:
            return {}

    def fill(self) -> None:
        if len(self.band) - 1 < self.position:
            self.band.append(self.initial["blank"])
        elif self.position < 0:
            self.band.insert(0, self.initial["blank"])
            self.position = 0

    def exec_instruction(self, instruction) -> None:

        if type(instruction) == str:
            instruction = {instruction: None}

        self.record()

        for k, v in instruction.items():

            match k:
                case "L":
                    self.position -= 1
                    if v:
                        self.state = v
                case "R":
                    self.position += 1
                    if v:
                        self.state = v
                case "write":
                    if v:
                        self.write(v)
                case _:
                    if self.read() == k:
                        self.exec_instruction(v)

            self.fill()

    def view(self) -> None:
        print("-" * 50)
        print("BAND : ", self.band)
        print("STATE : ", self.state)
        print("POSITION : ", self.position)

    def record(self) -> None:
        self.history.append(
            {
                "state": self.state,
                "reading": self.read(),
                "position": self.position,
                "memory": "".join(self.band),
                "transition": self.get_instruction(),
            }
        )

    def trim(self) -> None:
        i = 0
        while self.band[i] == self.initial["blank"]:
            self.band.pop(i)
            i += 1

        i = len(self.band) - 1
        while self.band[i] == self.initial["blank"]:
            self.band.pop(i)
            i -= 1


def run_turing_machine(
    machine: Dict,
    input_: str,
    steps: Optional[int] = None,
) -> Tuple[str, List, bool]:

    i = 0
    tmachine = TMachine(machine, input_)
    while not tmachine.state == "done" and (not steps or steps > i):
        tmachine.exec_instruction(tmachine.get_instruction())
        tmachine.view()

        i += 1

    tmachine.trim()

    return (
        "".join(tmachine.band),
        tmachine.history,
        True if tmachine.state == "done" else False,
    )