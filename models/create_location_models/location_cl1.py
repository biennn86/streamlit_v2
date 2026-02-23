from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_cl1() -> list:
	config_cl1 = [
		#CL1 FLOOR
		FloorConfig(
			location_name = ['PM' + str(i) + j for i in range(17, 20) for j in ['A', 'B']] +\
			 ['PM' + str(i) + j for i in range(23, 31) for j in ['A', 'B']] +\
			 ['PM17C'] + ['PM27'],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.COOL1_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL1,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#CL1 WW
		FloorConfig(
			location_name = ['FPM18', 'FPM19'],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.COOL1_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL1,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			)
	]

	return config_cl1