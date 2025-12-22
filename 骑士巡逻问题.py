def knight_tour(start_x,start_y,n):

    moves = [(1,2),(2,1),(2,-1),(1,-2),
             (-1,2),(-2,1),(-2,-1),(-1,-2),]    #给出骑士可以前进的方向

    board = [[{'pos':(x,y),'step':-1}for x in range(n)] for y in range(n)]    #生成一个二维数组作为棋盘，并给每个格子贴上标签，用-1表示已经走过，从而避免重复
    board[start_y][start_x]['step'] = 0    #初始位置标签为0

    def in_board(x,y):
        return 0<= x < n and 0<= y < n and board[y][x]['step'] == -1    #判断骑士是否在棋盘内

    def func(x,y,step):
        if step == n * n - 1 :
            return True    #当骑士走完所有格子时，终止循环

        for s1,s2 in moves:
            new_x,new_y = x+s1,y+s2    #穷举所有可能的方向
            if in_board(new_x,new_y):
                board[new_y][new_x]['step'] = step + 1    #每走一步，步数加一，这样可以记录下这个格子是第几步经过的
                if func(new_x,new_y,step + 1) :
                    return True
                board[new_y][new_x]['step'] = -1    #给走过的格子标记为-1
        return False

    if func (start_x,start_y,0):
        print("路径如下")
        for r in board:
            print(["{:>5}".format(f"{c['step']}") for c in r])  #输出路线
    else:
        print(" 无解")

knight_tour(3,2,6)