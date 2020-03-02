=========
Commander
=========

命令行解析框架,快速构建自己的脚手架命令行工具.

安装
----
https://github.com/RockJohnson503/commander/releases 下载wheel文件并使用pip安装.

快速开始
--------

文件目录::

    example/
        main.py
        commands/
            example.py
            test.py

main.py案例代码::

    # main.py
    import os
    from commander import execute_from_command_line

    # 传入commands的上级目录(example目录)
    # os.path.abspath(__file__)返回 xxx/example/main.py
    # os.path.dirname(os.path.abspath(__file__)) 返回 xxx/example
    execute_from_command_line(os.path.dirname(__file__))

shell调用::

    >> python main.py
    输入"main.py help <subcommand>"以获取子命令的帮助信息.

    可用子命令:

    test
    example
    >> python main.py test -h
    >> python main.py help example

编辑器直接运行main.py::

    # main.py
    import os
    from commander import execute_from_command_line

    # 传入commands的上级目录(example目录)
    # os.path.abspath(__file__)返回 xxx/example/main.py
    # os.path.dirname(os.path.abspath(__file__)) 返回 xxx/example
    execute_from_command_line(os.path.dirname(os.path.abspath(__file__)), 'my-program help')

输出::

    输入"my-program help <subcommand>"以获取子命令的帮助信息.

    可用子命令:

    test
    example

