Các biến quan trọng liên quan đến file gui.py

dòng 62: biến player_pos chứa vị trí hiện tại của player 
    +) Ví dụ: Trong file "input01.txt" thì vị trí của player sẽ là (x, y) với x là trục hoành (x=3), y là trục tung(y=4) => player_pos =(3,4)

dòng 65: biến stones là một dict với key là vị trí hiện tại của các stones và value là cân nặng tương ứng với từng stone
    +) Ví dụ: Trong file "input01.txt" có 2 stones :
        +) stone 1 : vị trí (2, 3) cân nặng 1
        +) stone 2 : vị trí (4, 3) cân nặng 9
        => biến stones = {(2, 3): 1, (4, 3): 99}

dòng 71: biến graph_way_nodes là biến chứa các node cha và node con của một ô đường đi
    +) Ví dụ: (1, 2): [(1, 3), (2, 2)]
              (1, 3): [(1, 2), (1, 4), (2, 3)]
              (1, 6): [(1, 5), (1, 7), (2, 6)]
              ........
            Node cha tại vị trí (1, 2) có các node con là (1, 3), (2, 2). Và tương tự cho các node khác. (Cái này là graph như học trong môn DSA).


dòng 225: biến way_player_go chứa các đường đi mà nhân vật sẽ đi (Không bao gồm vị trí hiện tại)

***************) Hướng dẫn sử dụng:
Mn nên chạy python gui.py để xem cách nhân vật di chuyển.