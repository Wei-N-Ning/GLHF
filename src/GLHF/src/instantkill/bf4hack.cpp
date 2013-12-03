// bf4hack.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"

#include "bf4classes.h"

#include <string>
#include <sstream>

// setting the no-recoil, no-spread and bullet-count attributes in the local soldier weapon block
bool PatchLocalSoldierWeaponStats(void)
{
	ClientGameContext* pGContext = ClientGameContext::GetInstance( );
	if ( !pGContext )
		return false;
	//OutputDebugStringA("@@ GOT Game Context");

	ClientPlayerManager* pCPM = pGContext->m_pPlayerManager;
	if ( !pCPM )
		return false;
	//OutputDebugStringA("@@ GOT Player Manager");

	ClientPlayer* pLocalPlayer = pCPM->m_pLocalPlayer;
	if ( !pLocalPlayer )
		return false;
	//OutputDebugStringA("@@ GOT Client local player");

	// if (InVehicle() == true)
	if ( pLocalPlayer->m_pAttachedControllable != NULL )
		return false;
	//OutputDebugStringA("@@ Not In Vehicle");

	ClientSoldierEntity* pCSE = pLocalPlayer->m_pControlledControllable;
	if ( !pCSE )
		return false;
	//OutputDebugStringA("@@ GOT Client Soldier Entity");

	// check health making sure the local soldier is alive!
	ClientControllableEntity::HealthComponent* pHP = pCSE->m_pHealthComponent;
	if ( pHP->m_vehicleHealth < 0.1 )
		return false;
	//OutputDebugStringA("@@ Is Alive");

	ClientSoldierWeaponsComponent* pCSWC = (ClientSoldierWeaponsComponent*)*(UINT64*)((UINT64)pCSE + 0x550);
	if ( !pCSWC )
		return false;
	//OutputDebugStringA("@@ GOT Client Soldier Weapon Component");

	BYTE activeSlot = *(BYTE*)((UINT64)pCSWC + 0x09A8);
	if ( !(activeSlot == 0 || activeSlot == 1) )
		return false;
	//OutputDebugStringA("@@ current weapon is a primary or secondary weapon!");

	UINT64 weaponArrayBase = (UINT64)pCSWC->m_handler;
	ClientSoldierWeapon* pCSW = (ClientSoldierWeapon*)*(UINT64*)(weaponArrayBase + activeSlot * 8);
	//std::stringstream debugString;
	//debugString << "ClientSoldierWeapon: [" << std::hex << pCSW << ']' << std::endl;
	//OutputDebugStringA(debugString.str().c_str());
	//debugString.clear();

	if ( !pCSW )
		return false;
	//OutputDebugStringA("@@ GOT Client Soldier Weapon!");

	// ------------------------
	// note: after a few respawn the following logic does not work!!!
	// ------------------------

	WeaponFiring* pWF = pCSW->m_Primary;
	//debugString << "WeaponFiring: [" << std::hex << pWF << ']' << std::endl;
	//OutputDebugStringA(debugString.str().c_str());
	//debugString.clear();

	if ( !pWF )
		return false;
	// ------------------------
	// note: instant kill
	// ------------------------
	PrimaryFire* pPF = pWF->m_pPrimaryFire;
	if ( !pPF )
		return false;

	ShotConfigData* pSCD = pPF->m_shotConfigData;
	if ( !pSCD )
		return false;

	pSCD->m_numberOfBulletsPerShell = 5;

	return true;

	//OutputDebugStringA("@@ GOT Weapon Firing!");

	WeaponSway* pSway = pWF->m_pSway;
	//debugString << "Sway: [" << std::hex << pSway << ']' << std::endl;
	//OutputDebugStringA(debugString.str().c_str());

	if ( ((UINT64)pSway & 0x0000000FF0000000) != ((UINT64)pWF & 0x0000000FF0000000) )
		if ( !pSway || (UINT64)pSway > 0xF0000000 || (UINT64)pSway < 0x10000000)
			return false;
	//OutputDebugStringA("@@ GOT -legit- Sway!");
	//OutputDebugStringA("@@ Patching!!!!");
	
	// patching

	// ----------------------
	// note: it changes the crosshair, only use it in hardcore mode for now!!
	// ----------------------

	// only visual??
	pSway->m_deviationPitch = 0.00001f;
	pSway->m_deviationYaw = 0.00001f;
	pSway->m_deviationRoll = 0.00001f;
	pSway->m_deviationTransY = 0.00001f;
	
	pSway->m_currentDispersionPitch = 0.00001f;
	pSway->m_currentDispersionYaw = 0.00001f;
	pSway->m_currentDispersionRoll = 0.00001f;
	pSway->m_currentDispersionTransY = 0.00001f;
	
	// does the real work
	pSway->m_dispersionAngle = 0.00001f;
	pSway->m_minDispersionAngle = 0.00001f;

	return true;
}



// use game time!!
void RunPatchingLogic(void)
{
	while (1)
	{
		bool result = PatchLocalSoldierWeaponStats();
		if ( !result )
			Sleep(500);
		else
			Sleep(50);
		//Sleep(10); // 1000.0 / 60.0 --> 15.6
	}
}