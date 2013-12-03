#ifndef BF4CLASSES_H
#define BF4CLASSES_H

#include <windows.h>

#include "offsets.h"


struct D3DXMATRIX
{
	float col1[4];
	float col2[4];
	float col3[4];
	float col4[4];
};


class ProjectileData
{
public:
    char pad_0x0000[288];
    DWORD unk; //0x0120 
    char pad_0x0124[44];
    float m_fUnk; //0x0150 
    float m_DamageMin; //0x0154 
    float m_DamageMax; //0x0158 
    float m_DamageFallOff; //0x015C 
    float m_DamageFallOffEndDistance; //0x0160 
    float m_TimeToArmExplosion; //0x0164 
    char pad_0x0168[4];
    BYTE m_bHasVehicleDetination; //0x016C 
    BYTE m_bInstantHit; //0x016D 
    BYTE m_bStopTrail; //0x016E 
    BYTE m_bUnk; //0x016F 
};

class ShotConfigData
{
public:
    char pad_0x0000[136];
    float m_initialSpeed; //0x0088 
    char pad_0x008C[20];
    float m_inheritWeaponSpeedAmount; //0x00A0 
    char pad_0x00A4[12];
    ProjectileData* m_pProjectileData; //0x00B0 
    ProjectileData* m_pSecondaryProjectileData; //0x00B8 
    __int64 m_projectile; //0x00C0 
    __int64 m_secondaryProjectile; //0x00C8 
    float m_spawnDelay; //0x00D0 
    DWORD m_numberOfBulletsPerShell; //0x00D4 
    DWORD m_numberOfBulletsPerShot; //0x00D8 
    DWORD m_numberOfBulletsPerBurst; //0x00DC 
    BYTE m_relativeTargetAiming; //0x00E0 
    BYTE m_forceSpawnToCamera; //0x00E1 
    BYTE m_spawnVisualAtWeaponBone; //0x00E2 
    BYTE m_activeForceSpawnToCamera; //0x00E3 
};//Size=0x00E4

class PrimaryFire
{
public:
    BYTE pad00[0x10];                    // 0x0000
    ShotConfigData* m_shotConfigData;    // 0x0010
};



class WeaponSway
{
public:
    char pad_0x0000[304];
    float m_deviationPitch; //0x0130 
    float m_deviationYaw; //0x0134 
    float m_deviationRoll; //0x0138 
    float m_deviationTransY; //0x013C 
    float m_timeSinceLastShot; //0x0140 
    DWORD m_cameraRecoilDeviation; //0x0144 
    D3DXMATRIX m_cameraRecoilTransform; //0x0148 
    char pad_0x0188[24];
    float m_dispersionAngle; //0x01A0 
    float m_minDispersionAngle; //0x01A4 
    float m_crossHairDispersionFactor; //0x01A8 
    float m_currentDispersionPitch; //0x01AC 
    float m_currentDispersionYaw; //0x01B0 
    float m_currentDispersionRoll; //0x01B4 
    float m_currentDispersionTransY; //0x01B8 
}; // Size 0x0438


class WeaponFiring
{
public:
    char pad_0x0000[120];
    WeaponSway* m_pSway; //0x0078 
    char pad_0x0080[168];
    PrimaryFire* m_pPrimaryFire; //0x0128 
    char pad_0x0130[24];
    DWORD m_weaponState; //0x0148 
    DWORD m_lastWeaponState; //0x014C 
    DWORD m_nextWeaponState; //0x0150 
    char pad_0x0154[8];
    float m_timeToWait; //0x015C 
    float m_reloadTimer; //0x0160 
    float m_holdReleaseMinDelay; //0x0164 
    float m_recoilTimer; //0x0168 
    float m_recoilAngleX; //0x016C 
    float m_recoilAngleY; //0x0170 
    float m_recoilAngleZ; //0x0174 
    float m_recoilFovAngle; //0x0178 
    float m_recoilTimeMultiplier; //0x017C 
    float m_overheatDropMultiplier; //0x0180 
    __int32 m_primaryAmmoToFill; //0x0184 
    __int32 m_reloadStage; //0x0188 
    DWORD_PTR m_pCharacterMeleeEntity; //0x018C 
    __int32 m_externalPrimaryMagazineCapacity; //0x0194 
    char pad_0x0198[8];
    __int32 m_projectilesLoaded; //0x01A0 
    __int32 m_projectilesInMagazines; //0x01A4 
    __int32 m_numberOfProjectilesToFire; //0x01A8 
    BYTE m_hasStoppedFiring; //0x01AC 
    BYTE m_primaryFireTriggeredLastFrame; //0x01AD 
    BYTE m_isOverheated; //0x01AE 
    BYTE m_unknown; //0x01AF 
    char pad_0x01B0[8];
    DWORD m_tickCounter; //0x01B8 
    __int32 m_fireMode; //0x01BC 
    char pad_0x01C0[8];
    DWORD_PTR m_pFiringHolderData; //0x01C8 
};


class ClientSoldierWeapon
{
public:
    BYTE pad00[0x49C0];            // 0x49C0
    WeaponFiring* m_Primary;    // 0x49C8
};


class ClientSoldierWeaponsComponent
{
public:

    class ClientAnimatedSoldierWeaponHandler
    {
    public:
        ClientSoldierWeapon* m_WeaponList[7]; //0x0000 
    }; 

    enum WeaponSlot
    {
        M_PRIMARY = 0, 
        M_SECONDARY = 1,
        M_GADGET = 2,
        M_GRENADE = 6,
        M_KNIFE = 7                 
    };

    char pad_0x0000[208];
    D3DXMATRIX m_weaponTransform; //0x00D0 
    char pad_0x0110[1680];
    ClientAnimatedSoldierWeaponHandler* m_handler; //0x07A0 
    char pad_0x07A8[32];
    char _pad_ClientAntAnimatableComponent[8]; //ClientAntAnimatableComponent* m_animatableComponent[2]; //0x07C8 
    char _pad_ClientSoldierEntity[8]; //ClientSoldierEntity* m_soldier; //0x07D8 
    char pad_0x07E0[456];
    WeaponSlot m_activeSlot; //0x09A8
    WeaponSlot m_lastActiveSlot; //0x09AC 
    WeaponSlot m_lastActiveWeaponSlot; //0x09B0 
    char pad_0x09B4[28];
    int m_currentZoomLevel; //0x09D0 
    int m_zoomLevelMax; //0x09D4 
    int m_zeroingDistanceLevel; //0x09D8 
    BYTE m_noMagnifierAccessory; //0x09DC 
    char pad_0x09DD[779];
    float m_timeSinceLastShot; //0x0CE8 

    ClientSoldierWeapon* GetActiveSoldierWeapon( )
    {
        if ( m_activeSlot == 0 || m_activeSlot == 1 )
            return m_handler->m_WeaponList[m_activeSlot];
        else
            return NULL;
    };
};


class ClientControllableEntity
{
public:

    class HealthComponent
    {
    public:
        char pad_0x0000[32];
        float m_health; //0x0020 
        float m_maxhealth; //0x0024 
        char pad_0x0028[16];
        float m_vehicleHealth; //0x0038 
    };
    
    virtual void Function0( ); //
    virtual void Function1( ); //
    virtual void Function2( ); //
    virtual void Function3( ); //
    virtual void Function4( ); //
    virtual void Function5( ); //
    virtual void Function6( ); //
    virtual void Function7( ); //
    virtual void Function8( ); //
    virtual void Function9( ); //
    virtual void Function10( ); //
    virtual void Function11( ); //
    virtual void Function12( ); //
    virtual void Function13( ); //
    virtual void Function14( ); //
    virtual void Function15( ); //
    virtual void Function16( ); //
    virtual void Function17( ); //
    virtual void Function18( ); //
    virtual void Function19( ); //
    virtual void Function20( ); //
    virtual void Function21( ); //
    virtual void Function22( ); //
    virtual void GetTransform( D3DXMATRIX* mTransform ); // ClientControllableEntity
    
    char pad_0x0008[248];
    float m_velocity; //0x0100 
    char pad_0x0104[60];
    HealthComponent* m_pHealthComponent; //0x0140 
    char pad_0x0148[64];
};


class ClientCharacterEntity : public ClientControllableEntity
{
public:
    char pad_0x0188[80]; //72 with vt?
    char _pad_ClientPlayer[8]; //ClientPlayer* m_pPlayer; //0x01D8 
    char _pad_ClientAntAnimatableComponent[8]; //ClientAntAnimatableComponent* m_animatableComponent[2]; //0x01E0 
    __int64 m_pCharacterCameraComponent; //0x01F0 
    char pad_0x01F8[136];
};


class SoldierEntity
{
public:
    char pad_0x0000[256];
    __int64 m_pBoneCollisionComponent; //0x0100 
    float m_moveSpeedMultiplier; //0x0108 
    float m_sprintSpeedMultiplier; //0x010C 
    float m_jumpHeightMultiplier; //0x0110 
    float m_lookSpeedMultiplier; //0x0114 
    float m_waterLevel; //0x0118 
    float m_waterSpeed; //0x011C 
    char pad_0x0120[8];
    __int64 m_pCharacterEntity; //0x0128 
};


class ClientSoldierEntity : public ClientCharacterEntity,    // +0x000
                            public SoldierEntity            // +0x280
{    
public:

    class BreathControlHandler
    {
    public:
        char pad_0x0000[56];
        float m_breathControlTimer; //0x0038 
        float m_breathControlMultiplier; //0x003C 
        float m_breathControlPenaltyTimer; //0x0040 
        float m_breathControlPenaltyMultiplier; //0x0044 
        float m_breathControlActive; //0x0048 
        float m_breathControlInput; //0x004C 
    };

    class SprintInputHandler
    {
    public:
        __int32 m_currentState; //0x0000 
        float m_doubleTapTimer; //0x0004 
        float m_sprintReleaseTimer; //0x0008 
        __int32 m_waitForSprintRelease; //0x000C 
    };

    char pad_0x03B0[216];
    __int64 m_pVehicleEntry; //0x0488 
    char _pad_ClientSoldierPredication[8]; //ClientSoldierPrediction* m_pPredictedController; //0x0490 
    char pad_0x0498[64];
    float m_authorativeYaw; //0x04D8 
    float m_authorativePitch; //0x04DC 
    __int32 m_aimingEnabled; //0x04E0 
    float m_cachedPitch; //0x04E4 
    __int64 m_soldierSound; //0x04E8 
    __int32 m_poseType; //0x04F0 
    char pad_0x04F4[92];
    ClientSoldierWeaponsComponent* m_soldierWeaponsComponent; //0x0550 
    __int64 m_bodyComponent; //0x0558 
    char _pad_ClientRagDollComponent[8]; //ClientRagDollComponent* m_ragdollComponent; //0x0560 
    BreathControlHandler* m_breathControlHandler; //0x0568 
    char pad_0x0570[16];
    SprintInputHandler* m_sprintInputHandler; //0x0580 
    __int32 padThis; //0x0588 
    float m_timeSinceLastSprinted; //0x058C 
    BYTE m_sprinting; //0x0590 
    BYTE m_occluded; //0x0591 
    char pad_0x0592[286];
    __int64 m_pClientCharacterEntity; //0x06B0 
    char pad_0x06B8[416];

    bool Visible( )
    {
        return !m_occluded;
    }

    ClientSoldierWeapon* GetActiveWeapon( )
    {
        if ( !m_soldierWeaponsComponent )
            return NULL;    
        if ( ( DWORD_PTR )m_soldierWeaponsComponent > 0xFFFFFFFF )
            return NULL;
        if ( IsBadReadPtr( m_soldierWeaponsComponent, 8 ) )
            return NULL;
        return m_soldierWeaponsComponent->GetActiveSoldierWeapon( );
    }
};


class ClientPlayer
{
public:
    virtual void Function0( ); 
    virtual DWORD_PTR GetCharacterEntity( ); // ClientSoldierEntity + 188 
    virtual DWORD_PTR GetCharacterUserData( ); // PlayerCharacterUserData
    virtual DWORD_PTR GetEntryComponent( );
    virtual bool InVehicle( );

    BYTE pad00[0x38];                                // 0x000
    CHAR szName[0x10];                                // 0x040
    BYTE pad38[0xC6C];                                // 0x050
    int m_teamId;                                    // 0xCBC
    BYTE padB34[0xF0];                                // 0xCC0
    ClientSoldierEntity* m_pAttachedControllable;    // 0xDB0
    unsigned int m_attachedEntryId;                    // 0xDB8
    ClientSoldierEntity* m_pControlledControllable;    // 0xDC0

    ClientSoldierEntity* GetClientSoldier( )
    {
        if ( this->InVehicle( ) )
            return ( ClientSoldierEntity* )( this->GetCharacterUserData( ) - 0x290 );

        if ( m_pControlledControllable )
            return m_pControlledControllable;

        return NULL;
    }
};


class ClientPlayerManager
{
public:
    BYTE pad00[0x2A0];                  // 0x00
    ClientPlayer*    m_pLocalPlayer;        // 0x2A0
    ClientPlayer**    m_ppPlayers;        // 0x2A8

    ClientPlayer* GetPlayerById( unsigned int id )
    {
        if ( id < 70 )
            return this->m_ppPlayers[id];

        return NULL;
    }
};


class ClientGameContext
{
public:
    BYTE pad00[0x20];                        // 0x00
    DWORD_PTR m_GameTime;                    // 0x20
    char _pad_Level[8]; //Level* m_Level;                            // 0x28
    BYTE pad30[0x30];                        // 0x30
    ClientPlayerManager* m_pPlayerManager;    // 0x60

    static ClientGameContext* GetInstance( )
    {
		return *( ClientGameContext** )( GAME_CONTEXT_PTR_ADDRESS );
    }
};


#endif