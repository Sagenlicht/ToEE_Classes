from templeplus.pymod import PythonModifier
from toee import *
import tpdp
import char_class_utils

###################################################

def GetConditionName():
    return "Stormlord"

def GetSpellCasterConditionName():
    return "Stormlord Spellcasting"
    
print "Registering {}".format(GetConditionName())

classEnum = stat_level_stormlord
classSpecModule = __import__('class038_stormlord')
###################################################


#### standard callbacks - BAB and Save values
def OnGetToHitBonusBase(attachee, args, evt_obj):
    classLvl = attachee.stat_level_get(classEnum)
    babvalue = game.get_bab_for_class(classEnum, classLvl)
    evt_obj.bonus_list.add(babvalue, 0, 137) # untyped, description: "Class"
    return 0

def OnGetSaveThrowFort(attachee, args, evt_obj):
    value = char_class_utils.SavingThrowLevel(classEnum, attachee, D20_Save_Fortitude)
    evt_obj.bonus_list.add(value, 0, 137)
    return 0

def OnGetSaveThrowReflex(attachee, args, evt_obj):
    value = char_class_utils.SavingThrowLevel(classEnum, attachee, D20_Save_Reflex)
    evt_obj.bonus_list.add(value, 0, 137)
    return 0

def OnGetSaveThrowWill(attachee, args, evt_obj):
    value = char_class_utils.SavingThrowLevel(classEnum, attachee, D20_Save_Will)
    evt_obj.bonus_list.add(value, 0, 137)
    return 0

classSpecObj = PythonModifier(GetConditionName(), 0)
classSpecObj.AddHook(ET_OnToHitBonusBase, EK_NONE, OnGetToHitBonusBase, ())
classSpecObj.AddHook(ET_OnSaveThrowLevel, EK_SAVE_FORTITUDE, OnGetSaveThrowFort, ())
classSpecObj.AddHook(ET_OnSaveThrowLevel, EK_SAVE_REFLEX, OnGetSaveThrowReflex, ())
classSpecObj.AddHook(ET_OnSaveThrowLevel, EK_SAVE_WILL, OnGetSaveThrowWill, ())

## Stormlord Feats

def stormlordWeapons():
    weaponList = [wt_javelin, wt_longspear, wt_shortspear, wt_spear]
    return weaponList

def featEnhancedJavelinsToHit(attachee, args, evt_obj):
    usedWeapon = evt_obj.attack_packet.get_weapon_used()
    if usedWeapon.obj_get_int(obj_f_weapon_type) == wt_javelin:
        classLevel = attachee.stat_level_get(classEnum)
        if classLevel < 6:
            enhancementBonus = 1
        elif classLevel < 10:
            enhancementBonus = 2
        else:
            enhancementBonus = 3
        evt_obj.bonus_list.add_from_feat(enhancementBonus, 12, 114, "Stormlord Enhanced Javelins")
    return 0

def featEnhancedJavelinsDamage(attachee, args, evt_obj):
    usedWeapon = evt_obj.attack_packet.get_weapon_used()
    if usedWeapon.obj_get_int(obj_f_weapon_type) == wt_javelin:
        classLevel = attachee.stat_level_get(classEnum)
        if classLevel < 6:
            enhancementBonus = 1
        elif classLevel < 10:
            enhancementBonus = 2
        else:
            enhancementBonus = 3
        if not evt_obj.damage_packet.attack_power & D20DAP_MAGIC:
            evt_obj.damage_packet.attack_power |= D20DAP_MAGIC
        evt_obj.damage_packet.bonus_list.add(enhancementBonus, 12, "~Enhancement~[TAG_ENHANCEMENT_BONUS] : ~Stormlord Enhanced Javelins~[TAG_CLASS_FEATURES_STORMLORD_ENHANCED_JAVELINS]")
        #evt_obj.damage_packet.bonus_list.add_from_feat(enhancementBonus, 12, 114, "Stormlord Enhanced Javelins")
    return 0

enhancedJavelins = PythonModifier("Stormlord Enhanced Javelins Feat", 0)
enhancedJavelins.MapToFeat("Stormlord Enhanced Javelins")
enhancedJavelins.AddHook(ET_OnToHitBonus2, EK_NONE, featEnhancedJavelinsToHit, ())
enhancedJavelins.AddHook(ET_OnDealingDamage, EK_NONE, featEnhancedJavelinsDamage, ())

def featResistanceToElectricity(attachee, args, evt_obj):
    classLevel = attachee.stat_level_get(classEnum)
    if classLevel >= 9:
        return 0
    if classLevel < 4:
        resistanceBonus = 5
    elif classLevel < 7:
        resistanceBonus = 10
    else:
        resistanceBonus = 15
    evt_obj.damage_packet.add_damage_resistance(resistanceBonus, D20DT_ELECTRICITY, 1010) #ID 1010 in damage.mes is Electricity
    return 0

electricityResistance = PythonModifier("Stormlord Resistance to Electricity Feat", 0)
electricityResistance.MapToFeat("Stormlord Resistance to Electricity")
electricityResistance.AddHook(ET_OnTakingDamage , EK_NONE, featResistanceToElectricity, ())

def featShockWeapon(attachee, args, evt_obj):
    usedWeapon = evt_obj.attack_packet.get_weapon_used()
    weaponList = stormlordWeapons()
    if not usedWeapon.obj_get_int(obj_f_weapon_type) in weaponList:
        return 0
    classLevel = attachee.stat_level_get(classEnum)
    bonusDice = dice_new('1d6')
    evt_obj.damage_packet.add_dice(bonusDice, D20DT_ELECTRICITY, 100) #ID 100 in damage.mes is Weapon
    if classLevel >= 8:
        if evt_obj.attack_packet.get_flags() & D20CAF_CRITICAL:
            bonusDiceBurst = dice_new('1d10')
            critMultiplier = evt_obj.damage_packet.critical_multiplier
            if critMultiplier > 3: #unsure if needed; D20SRD description ends at x4
                critMultiplier = 3
            bonusDiceBurst.number = critMultiplier
            print "bonusDiceBurst: {}".format(bonusDiceBurst)
            evt_obj.damage_packet.add_dice(bonusDiceBurst, D20DT_ELECTRICITY, 100) #ID 100 in damage.mes is Weapon
    return 0

shockWeapon = PythonModifier("Stormlord Shock Weapon Feat", 0)
shockWeapon.MapToFeat("Stormlord Shock Weapon")
shockWeapon.AddHook(ET_OnDealingDamage, EK_NONE, featShockWeapon, ())

def featThunderingWeaponDamage(attachee, args, evt_obj):
    usedWeapon = evt_obj.attack_packet.get_weapon_used()
    weaponList = stormlordWeapons()
    target = evt_obj.attack_packet.target
    if not usedWeapon.obj_get_int(obj_f_weapon_type) in weaponList:
        return 0
    print "passed weapon test"
    if evt_obj.attack_packet.get_flags() & D20CAF_CRITICAL:
        print "passed crit flag"
        bonusDice = dice_new('1d8')
        critMultiplier = evt_obj.damage_packet.critical_multiplier
        print "critMultiplier: {}".format(critMultiplier)
        if critMultiplier > 3: #unsure if needed; D20SRD description ends at x4
            critMultiplier = 3
        bonusDice.number = critMultiplier
        evt_obj.damage_packet.add_dice(bonusDice, D20DT_SONIC, 100) #ID 1012 in damage.mes is Weapon
        # Thundering Weapons deafens on a critical hit on a failed dc save 14
        saveDc = 14
        if target.saving_throw(saveDc, D20_Save_Fortitude, D20STD_F_SPELL_DESCRIPTOR_SONIC, attachee, EK_D20A_STANDARD_ATTACK):
            target.float_text_line("Not deafened")
        else:
            if target.condition_add_with_args('sp-Deafness', 0, 0, 0):
                game.particles('sp-Blindness-Deafness', target)
    return 0

thunderingWeapon = PythonModifier("Stormlord Thundering Weapon Feat", 0)
thunderingWeapon.MapToFeat("Stormlord Thundering Weapon")
thunderingWeapon.AddHook(ET_OnDealingDamage, EK_NONE, featThunderingWeaponDamage, ())

def featImmunityToElectricity(attachee, args, evt_obj):
    evt_obj.damage_packet.add_mod_factor(0.0, D20DT_ELECTRICITY, 132) #ID 132 in damage.mes is Immunity
    return 0

electricityImmunity = PythonModifier("Stormlord Immunity to Electricity Feat", 0)
electricityImmunity.MapToFeat("Stormlord Immunity to Electricity")
electricityImmunity.AddHook(ET_OnTakingDamage , EK_NONE, featImmunityToElectricity, ())

##### Spell casting

# configure the spell casting condition to hold the highest Divine classs
def OnAddSpellCasting(attachee, args, evt_obj):
    # arg0 holds the divine class
    if args.get_arg(0) == 0:
        args.set_arg(0, char_class_utils.GetHighestDivineClass(attachee))

    return 0

# Extend caster level for base casting class
def OnGetBaseCasterLevel(attachee, args, evt_obj):
    class_extended_1 = args.get_arg(0)
    class_code = evt_obj.arg0
    if class_code != class_extended_1:
        if evt_obj.arg1 == 0:  # arg1 != 0 means you're looking for this particular class's contribution
            return 0
    classLvl = attachee.stat_level_get(classEnum)
    evt_obj.bonus_list.add(classLvl , 0, 137)
    return 0


def OnSpellListExtensionGet(attachee, args, evt_obj):
    class_extended_1 = args.get_arg(0)
    class_code = evt_obj.arg0
    if class_code != class_extended_1:
        if evt_obj.arg1 == 0:  # arg1 != 0 means you're looking for this particular class's contribution
            return 0
    classLvl = attachee.stat_level_get(classEnum)
    evt_obj.bonus_list.add(classLvl, 0, 137)
    return 0


def OnInitLevelupSpellSelection(attachee, args, evt_obj):
    if evt_obj.arg0 != classEnum:
        return 0
    class_extended_1 = args.get_arg(0)
    classSpecModule.InitSpellSelection(attachee, class_extended_1)
    return 0


def OnLevelupSpellsCheckComplete(attachee, args, evt_obj):
    if evt_obj.arg0 != classEnum:
        return 0
    class_extended_1 = args.get_arg(0)
    if not classSpecModule.LevelupCheckSpells(attachee, class_extended_1):
        evt_obj.bonus_list.add(-1, 0, 137)  # denotes incomplete spell selection
    return 1


def OnLevelupSpellsFinalize(attachee, args, evt_obj):
    if evt_obj.arg0 != classEnum:
        return 0
    class_extended_1 = args.get_arg(0)
    classSpecModule.LevelupSpellsFinalize(attachee, class_extended_1)
    return 0


spellCasterSpecObj = PythonModifier(GetSpellCasterConditionName(), 8)
spellCasterSpecObj.AddHook(ET_OnConditionAdd, EK_NONE, OnAddSpellCasting, ())
spellCasterSpecObj.AddHook(ET_OnGetBaseCasterLevel, EK_NONE, OnGetBaseCasterLevel, ())
spellCasterSpecObj.AddHook(ET_OnSpellListExtensionGet, EK_NONE, OnSpellListExtensionGet, ())
spellCasterSpecObj.AddHook(ET_OnLevelupSystemEvent, EK_LVL_Spells_Activate, OnInitLevelupSpellSelection, ())
spellCasterSpecObj.AddHook(ET_OnLevelupSystemEvent, EK_LVL_Spells_Check_Complete, OnLevelupSpellsCheckComplete, ())
spellCasterSpecObj.AddHook(ET_OnLevelupSystemEvent, EK_LVL_Spells_Finalize, OnLevelupSpellsFinalize, ())
