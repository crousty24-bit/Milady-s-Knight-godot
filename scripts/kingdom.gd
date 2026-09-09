@tool
# Hand-placed pixel scenery. Pure drawing, no gameplay state or dynamic corruption.
extends Node2D
const FONT = preload("res://assets/fonts/PixelOperator8.ttf")
func block(x: float, y: float, w: float, h: float, color: String) -> void:
	draw_rect(Rect2(x,y,w,h),Color(color))
func tree(x: int, y: int, ruined: bool = false) -> void:
	var bark: String = "392e3d" if ruined else "393d36"
	block(x,y-64,5,64,bark)
	for i in range(3):
		var yy: int = y-30-i*13
		draw_line(Vector2(x+2,yy),Vector2(x-12,yy-14),Color(bark),3)
		draw_line(Vector2(x+3,yy-4),Vector2(x+19,yy-18),Color(bark),3)
	if not ruined:
		block(x-17,y-72,35,12,"354844")
		block(x-25,y-61,50,16,"3b5148")
		block(x-19,y-46,38,9,"43584b")
func house(x: int, y: int, ruined: bool = false) -> void:
	block(x,y-49,68,49,"5b5a50")
	block(x+3,y-47,62,46,"827765")
	block(x+5,y-45,58,41,"9b8b71")
	for yy in range(y-42,y,12): block(x+4,yy,59,2,"685f50")
	for xx in [x+4,x+32,x+61]:block(xx,y-46,3,46,"494740")
	draw_colored_polygon(PackedVector2Array([Vector2(x-8,y-48),Vector2(x+33,y-79),Vector2(x+76,y-48)]),Color("45454a"))
	for i in range(4):block(x-3+i*8,y-52-i*6,72-i*16,3,"6b6260")
	block(x+25,y-26,17,26,"292f32")
	block(x+10,y-32,10,13,"344344")
	block(x+48,y-32,10,13,"344344")
	if ruined:
		draw_line(Vector2(x+24,y-69),Vector2(x+48,y-48),Color("222c31"),6)
		draw_line(Vector2(x+30,y-46),Vector2(x+20,y-19),Color("393c39"),2)
	else: block(x+50,y-29,2,7,"c7a16a")
func _draw() -> void:
	block(-100,-400,2500,800,"18242c")
	block(-100,-16,2500,85,"26383f")
	block(-100,69,2500,210,"304448")
	# A pale broken moon and long clouds anchor the abandoned village.
	block(180,3,18,14,"acb6a5")
	block(176,7,25,7,"acb6a5")
	block(189,0,15,10,"26383f")
	for i in range(20):
		var x: int = i*123-20
		block(x,18+(i%3)*11,63,3,"34474b")
		block(x+25,14+(i%3)*11,44,4,"34474b")
	for i in range(16):
		var x: int = i*154-60
		draw_colored_polygon(PackedVector2Array([Vector2(x,126),Vector2(x+62,46+(i%3)*10),Vector2(x+145,126)]),Color("33494a"))
		block(x+57,68+(i%3)*10,12,58,"33494a")
	# Distant fortification, growing closer toward the exit.
	for x in range(1590,2280,72):
		block(x,34,52,150,"26363d")
		for xx in range(x,x+52,12):block(xx,27,7,10,"26363d")
		block(x+22,50,7,17,"172831")
	block(1570,94,740,120,"2a3a40")
	for i in range(24): tree(i*99+22,144,i>12)
	house(36,144)
	house(212,144,true)
	# Cart and its spilled cargo.
	block(407,126,34,9,"695b44")
	draw_circle(Vector2(413,139),5,Color("282e30"))
	draw_circle(Vector2(435,139),5,Color("282e30"))
	draw_circle(Vector2(413,139),2,Color("9a8861"))
	draw_circle(Vector2(435,139),2,Color("9a8861"))
	draw_line(Vector2(439,131),Vector2(458,136),Color("8b7757"),2)
	block(399,139,6,4,"9a8861")
	# Two-path sign. Visible before committing to either route.
	block(481,112,3,31,"806b50")
	block(463,106,38,8,"685b48")
	draw_string(FONT,Vector2(467,113),"12 OR >",HORIZONTAL_ALIGNMENT_LEFT,-1,8,Color("e2c989"))
	# Bridge pillars distinguish the high route from the lower road.
	for x in [706,780,986,1050,1130,1210]:
		block(x,88,9,136,"485454")
		for yy in range(92,224,12):block(x+1,yy,7,1,"69716a")
	# Torn royal standard: second environmental clue.
	block(1048,3,2,43,"817b68")
	draw_colored_polygon(PackedVector2Array([Vector2(1050,5),Vector2(1070,5),Vector2(1070,18),Vector2(1064,15),Vector2(1061,22),Vector2(1057,18),Vector2(1050,20)]),Color("705365"))
	block(1055,8,8,2,"bc9d6b")
	block(1058,7,2,8,"bc9d6b")
	# Corruption is sparse at first, dense close to the sealed wall.
	for i in range(22):
		var x: int = 1390+i*37
		var height: int = 12+(i*13)%39
		draw_line(Vector2(x,144),Vector2(x+7,144-height),Color("55435c"),3)
		draw_line(Vector2(x+3,136),Vector2(x-10,126),Color("69506d"),2)
		block(x+4,144-height,3,3,"b18bae")
	# Final wall and columns frame the actual gate, which draws in front.
	for x in range(1968,2232,16):
		if x>2040 and x<2104: continue
		for y in range(16,144,8):
			block(x+(8 if y%16 else 0),y,15,7,"4b5154")
			block(x+(8 if y%16 else 0),y,15,1,"666967")
	for x in range(1968,2240,24):block(x,8,12,9,"5f6665")
	# Princess's ribbon caught on a spear; no dialogue system needed.
	block(1892,107,2,37,"a39b7b")
	draw_colored_polygon(PackedVector2Array([Vector2(1889,110),Vector2(1893,101),Vector2(1896,110)]),Color("c1c5af"))
	draw_line(Vector2(1894,116),Vector2(1908,118),Color("c59ba7"),3)
	draw_line(Vector2(1908,118),Vector2(1914,124),Color("c59ba7"),2)
	# Terrain underlay and grass/small stones at safe, common ground.
	for x in range(4,480,21):
		block(x,141,3,3,"818458")
		block(x+3,139,1,5,"818458")
	for x in range(1415,1930,27):block(x,142,4,2,"807c78")
