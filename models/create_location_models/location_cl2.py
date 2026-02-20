from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_cl2() -> list:
	config_cl2 = [
		#CL2 FLOOR
		FloorConfig(
			location_name = ['PC' + str(i) + str(j) for i in [1, 31] for j in ['A']] +\
			 ['PC' + str(i) + str(j) for i in [18] for j in ['C', 'D']] +\
			 ['PC' + str(i) + str(j) for i in range(2, 31) for j in ['A', 'B']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.COOL2_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL2,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#CL2 WW
		FloorConfig(
			location_name = ['COOL1', 'COOL2', 'COOL3'],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.COOL2_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL2,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			)
	]

	return config_cl2