def overlap(x1,x2,y1,y2):
    if y1 > x2: return 0
    if x1 > y2: return 0
    l2len = y2 - y1
    if x1 < y1 and x2 > y2: return l2len
    res = l2len
    if x1 > y1:
        res = l2len + (y1 - x1)
    if x2 < y2:
        res -= y2 - x2
    if res > l2len: res = l2len
    return res

if __name__ == "__main__":
    assert(overlap(0,20,40,60) == 0)
    assert(overlap(0,20,18,60) == 2)
    assert(overlap(0,20,10,60) == 10)
    assert(overlap(20,22,0,6) == 0)
    assert(overlap(20,100,0,6) == 0)
    assert(overlap(0,100,0,6) == 6)
    assert(overlap(50,100,50,100) == 50)
    assert(overlap(49,100,50,100) == 50)
    assert(overlap(49,100,48,100) == 51)
    assert(overlap(134,143,132,159) == 9)
    assert(overlap(134,143,135,137) == 2)
    assert(overlap(134,143,133,135) == 1)
