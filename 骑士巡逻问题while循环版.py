def knight_tour(start_x, start_y, n):

    moves = [(1, 2), (2, 1), (2, -1), (1, -2),
             (-1, 2), (-2, 1), (-2, -1), (-1, -2), ]

    board = [[{'pos': (x, y), 'step': -1, 'move_index':0} for x in range(n)] for y in range(n)]  # 生成一个二维数组作为棋盘，并给每个格子贴上标签，用-1表示已经走过，从而避免重复
    board[start_y][start_x]['step'] = 0  # 初始位置标签为0

    stack = [(start_y, start_x)]
    step = 0

    def in_board(x,y):
        return 0<= x < n and 0<= y < n and board[y][x]['step'] == -1

    while stack:
        x,y = stack[-1]
        if step == n*n - 1:
            break

        move_i = board[y][x]['move_index']

        if move_i >= len(moves):
            board[y][x]['step'] = -1
            board[y][x]['move_index'] = 0
            stack.pop()
            step -= 1
            continue

        dx, dy = moves[move_i]
        new_x, new_y = x + dx, y + dy
        board[y][x]['move_index'] += 1

        if in_board(new_x, new_y):
            step += 1
            board[new_y][new_x]['step'] = step
            stack.append((new_y, new_x))

    if step != n*n - 1:
        print("无解")

    else:
        for r in board:
            print(["{:>5".format(f"{c['pos']}:{c['step']}")for c in r])


knight_tour(1, 1, 4)