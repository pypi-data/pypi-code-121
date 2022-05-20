import surfa as sf


vol = sf.io.load_volume('orig.mgz')
vol.save('resave.mgz')