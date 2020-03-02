from commander.base import BaseCommand


class Command(BaseCommand):
    help = "这是一个案例命令,返回面积."

    def add_arguments(self, parser):
        parser.add_argument('width', type=int, help='宽度')
        parser.add_argument('height', type=int, help='高度')
        parser.add_argument('-v', '--verbosity', default=0, action='count', help='0: 极简,1: 普通,2: 详细.')


    def handle(self, **options):
        answer = options["width"] * options["height"]
        if options['verbosity'] >= 2:
            return f'宽度: {options["width"]}, 高度: {options["height"]}, 面积: {answer}'
        elif options['verbosity'] >= 1:
            return f'{options["width"]} * {options["height"]} = {answer}'
        else:
            return answer
