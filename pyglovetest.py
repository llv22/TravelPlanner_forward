import pyglove as pg

@pg.members([
    ('name', pg.typing.Str().noneable()),
    ('time', pg.typing.Int().noneable() | pg.typing.Str().noneable()),
])
class Test(pg.Object):
    def __call__(self):
        print(f'Hello {self.name}! It is {self.time} o\'clock.')

t1 = Test('timothy', 12)
pg.patching.patch_on_key(t1, 'name', 'tim')
t2 = Test(t1.name, "twelve")

print(t1.__dict__["_sym_attributes"])
t2()