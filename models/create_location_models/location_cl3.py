from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_cl3() -> list:
	config_cl3 = [
		#CL3 FLOOR
		FloorConfig(
			location_name = ['EZ' + str(i).zfill(2) for i in range(1, 16) if i != 12] + ['EZ' + str(i) + str(j) for i in [12] for j in ['A', 'B', 'C']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.COOL3_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL3,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#CL3 RACK
		FloorConfig(
			location_name = ['EZ' + str(i) + str(j) for i in range(15, 24) for j in ['A', 'B']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.ST,
			location_storage_type = KeyLoc.LocStorageType.RACK_COOL,
			zone = KeyLoc.Zone.COOL3_RACK,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL3,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#CL3 WW
		FloorConfig(
			location_name = ['FEZ' + str(i).zfill(2) for i in [15, 17, 18, 19, 20, 21, 22, 23]],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.COOL3_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.COOL3,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			)
	]

	return config_cl3