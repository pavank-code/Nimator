class Test:
    pass

PROMPT = "global"

t = Test()
try:
    print(t.PROMPT)
except AttributeError:
    print("AttributeError caught")
