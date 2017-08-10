"""Wrapper script for seed cell size analysis."""

from smarttool import SmartTool


def main():

    tool = SmartTool()
    tool.container = "jicscicomp/seedcellsize"
    tool.command_string = "python /scripts/analysis.py -i /input1 -o /output"
    tool.outputs = [
        'original.png',
        'segmentation.png',
        'labels.png',
        'false_color.png',
        'results.csv'
    ]

    tool.run()


if __name__ == '__main__':
    main()
