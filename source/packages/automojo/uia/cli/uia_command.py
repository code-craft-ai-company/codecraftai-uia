
import sys
import os

# Add sources to path if running directly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../")))

from automojo.arcli.model.entrycommand import EntryCommand
from automojo.uia.cli.cmdtree.mapping import MappingCommand

class UiaCommand(EntryCommand):
    
    def __init__(self):
        super().__init__("uia", self.execute)
        self.add_command(MappingCommand())

    def execute(self, context):
        pass

def main():
    cmd = UiaCommand()
    cmd(args=sys.argv[1:])

if __name__ == "__main__":
    main()
