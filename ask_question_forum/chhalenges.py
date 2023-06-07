def fizz_buzz():
    for i in range(100):
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        elif i % 3 == 0:
            print("fizz")
        elif i % 5 == 0:
            print("fizz")
        else:
            print(i)


def palindrom_checker(my_str):
    my_str_1 = list(my_str)
    my_str_2 = list(reversed(my_str_1))
    return my_str_1 == my_str_2


def balanced(str_):
    my_list = list(str_)
    new_list = []
    a = [i for i in my_list if i == '(']
    b = [i for i in my_list if i == ')']
    if len(a) != len(b):
        return False
    for i in my_list:
        if i == '(':
            new_list.append(1)
        else:
            new_list.append(0)
    for i in new_list:
        if i == 1:
            num = 0
            for j in new_list[new_list.index(i):]:
                if j == 0:
                    num += 1
                    new_list.pop(new_list.index(j))
                    break
            if num == 0:
                return False
    return True

print(balanced("(()))"))
