class Microware:
	def __init__(self, brand: str, power_rating: str) -> None:
		self.brand = brand
		self.power_rating = power_rating


smeg: Microware = Microware(brand='Smeg', power_rating='B')

print(smeg)
print(smeg.brand)
print(smeg.power_rating)
