from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_pf1() -> list:
	# Thêm dòng import ngay tại đây để tránh Circular Import
	config_pf1 = [
		#PF1
		FloorConfig(
			location_name = ['Z1' + str(i).zfill(2) + j for i in range(4, 13) for j in ['A', 'B']],
			location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF1_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF1,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#PF1 WW
		FloorConfig(
			location_name = ['FZ1' + str(i).zfill(2) for i in range(8, 13)],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF1_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF1,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			)
	]

	return config_pf1
