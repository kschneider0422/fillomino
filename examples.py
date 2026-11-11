from fillomino import Fillomino


# dims = (6, 6)
# givens = {(0, 1): 3, (0, 2): 5,
#           (1, 0): 3, (1, 1): 2, (1, 3): 3, (1, 5): 2,
#           (2, 2): 9, (2, 3): 9, (2, 5): 2,
#           (3, 1): 9,
#           (4, 2): 3, (4, 3): 5, 
#           (5, 0): 1, (5, 1): 2, (5, 2): 3, (5, 5): 1,}

# F = Fillomino(dims, givens)
# F.solve()
# F.board.plot()
# F.solutions[0].plot()


raw = '''	1	6	1	6		1		1				1	8				6		3
				1				3		5		3				1		3	
1	6				3			1		4	3	1		1		4			2
				3	1		1			1			1	4		1		1	2
	6	8	1			5					6	7		1					
	1				1			1		6		1				9			
	6		7	1			8						1	6			5	5	5
			5				1	3	1	8				6	6	1		5	1
1			1			1		1		6	1		1				1		
		1			1	5							3						7
		6		4	6		5	1	5				3	3	1	8	1		
	1		1					4		1	5	1							1
1	3			1	5	5				3	1		4					1	
5		1						1		1				6	9	1			
	1	6	6	6		3	1		1	6				1	4	4	7		2
					3	1		6	6			1					4	1	
1		1	8					6	6		1		1				5		
		9	1		1				9		2			1	9			5	
				5	5				7					2			1		
		1		5				1	3		1	6	1		1		4	3	1'''
        
grid = [[None if _ == '' else int(_) for _ in row.split('\t')] for row in raw.split('\n')]
rows = len(grid)
cols = len(grid[0])
dims = (rows, cols)
givens = {(r, c): grid[r][c] for r in range(rows) for c in range(cols) if grid[r][c] is not None}

F = Fillomino(dims, givens)
# F.solve()
F.board.plot()
# F.solutions[0].plot()