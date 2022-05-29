f = lambda module_names: ['src.jfts.'+m for m in module_names]
t = lambda: ['src.jfts.abc', 'src.jfts.xyz'] == f(['abc', 'xyz'])