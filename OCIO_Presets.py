# SPDX-License-Identifier: BSD-3-Clause
# mrv2
# Copyright Contributors to the mrv2 Project. All rights reserved.

#
# For this example, we will just use the timeline module.           #   TODO
#


##  version 0.2 beta

import os
import json
import functools

import mrv2
import fltk14 as fltk

PLUGINPATH = os.path.dirname(__file__)
SETTINGSFILE = os.path.join(PLUGINPATH,
                            "OCIO_Presets",
                            "ocioPresetsConfig.json")



class OcioPresetsPlugin(mrv2.plugin.Plugin):
    def __init__(self):
        super().__init__()

        self.presetList = []
        self.loadSettings()


    def active(self):
        return True


    # def on_open_file(self, filename, audioFileName):
    #     """
    #     Callback called when a file is opened.
    #     """
    #     pass


    def loadSettings(self):
        if os.path.exists(SETTINGSFILE):
            try:
                with open(SETTINGSFILE, 'r') as file:
                    self.presetList = json.load(file)
                # print(f"Preset list loaded from {SETTINGSFILE}")
            except FileNotFoundError:
                pass
                # print(f"No settings file found at {SETTINGSFILE}, starting with an empty preset list.")
            except Exception as e:
                print(f"An error occurred while loading the preset list: {e}")


    def saveSettings(self):
        settingsDir = os.path.dirname(SETTINGSFILE)
        if not os.path.exists(settingsDir):
            os.mkdir(settingsDir)

        try:
            with open(SETTINGSFILE, 'w') as file:
                json.dump(self.presetList, file, indent=4)
            # print(f"Preset list saved to {SETTINGSFILE}")
        except Exception as e:
            print(f"An error occurred while saving the preset list: {e}")

    
    def getCurrentConfig(self):
        self.currConfigFile = mrv2.image.ocioConfig()
        print(self.currConfigFile)


    def getCurrTransforms(self):
        currIDT = mrv2.image.ocioIcs()
        currODT = mrv2.image.ocioView()
        currLook = mrv2.image.ocioLook()

        return currIDT, currODT, currLook
    

    def savePreset(self):
            currIDT, currODT, currLook = self.getCurrTransforms()
            # presetName = currIDT + "-" + currODT + "-" + currLook

            # Check if presetName already exists in presetList
            # for preset in self.presetList:
            #     if preset["name"] == presetName:
            #         print(f"Preset '{presetName}' already exists. Not saving.")
            #         return

            # Function to create and handle FLTK dialog
            def createPresetDialog():
                dialog = fltk.Fl_Window(500, 150, "Enter Preset Name")
                dialog.set_non_modal()  # To stay on top

                label_width = 120
                inputBox = fltk.Fl_Input(label_width + 20, 40, 430 - label_width, 30, "Preset Name:")
                inputBox.textcolor(fltk.FL_BLACK)

                def onOkButtonClicked(button, inputBox):
                    newPresetName = inputBox.value()
                    # print(f"New preset name entered: {new_preset_name}")
                    # Perform actions with the entered preset name
                    preset = {
                        "order": self.getNextPresetNumber(),
                        "name": newPresetName,
                        "IDT": currIDT,
                        "ODT": currODT,
                        "Look": currLook
                    }
                    self.presetList.append(preset)   # Append updated preset
                    self.saveSettings()              # Save updated preset list
                    self.refreshMenus()              # Refresh menus after update
                    dialog.hide()                    # Close the dialog window

                ok_button = fltk.Fl_Button(120, 90, 60, 30, "OK")
                ok_button.callback(onOkButtonClicked, inputBox)

                dialog.end()
                dialog.show()
                fltk.Fl.run()

            # Call the dialog creation function
            createPresetDialog()


    def getPresetNames(self):
        presetNames = []
        for preset in self.presetList:
            name = preset["name"].replace("/", "-")
            presetNames.append(name)

        return presetNames
    

    def getNextPresetNumber(self):
        if not self.presetList:
            return 1
        
        highest = max(self.presetList, key=lambda x: x["order"])["order"]
        nextNumber = highest + 1

        return nextNumber
    

    def getTransformsFromName(self, presetName):
        for preset in self.presetList:
            if preset["name"].replace("/", "-") == presetName:
                idt = preset["IDT"]
                odt = preset["ODT"]
                look = preset["Look"]
                break

        return idt, odt, look


    def applyPreset(self, presetName):
        idt, odt, look = self.getTransformsFromName(presetName)

        mrv2.image.setOcioIcs(idt)
        mrv2.image.setOcioView(odt)
        mrv2.image.setOcioLook(look)

        # print(f"Applied preset: {presetName}")


    def removePreset(self, presetName):
        # print(f"Removing preset: {presetName}")
        
        # Iterate over presetList to find and remove the preset
        for preset in self.presetList:
            if preset["name"].replace("/", "-") == presetName:
                self.presetList.remove(preset)
                # print(f"Preset '{presetName}' removed.")
                break  # Exit loop after removing the preset
        
        self.saveSettings()  # Save updated presetList to file
        self.refreshMenus()


    def refreshMenus(self):             #   TODO
        mrv2.menus = self.menus()


    def menus(self):
        menus = {}
        presetNames = self.getPresetNames()

        for name in presetNames:
            menus[f"OCIO/Presets/{name}"] = functools.partial(self.applyPreset, name)

        menus["OCIO/Current OCIO Config"] = self.getCurrentConfig
        menus["OCIO/Save Preset"] = self.savePreset

        for name in presetNames:
            menus[f"OCIO/Remove Preset/{name}"] = functools.partial(self.removePreset, name)

        return menus