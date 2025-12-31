## Styles Improvements
- Add `BotLink` style for invitation links, for example:
    ```py
    BotLink(Bold("Invitation link"), bot_id=self.bot.get_me().id, start="INVITE_CODE")
    BotLink(Bold("Invitation link"), bot_id=self.bot.get_me().username, start="INVITE_CODE")
    ```

## DSL Improvements
- Add a new `ScriptData` class to group all script data and new methods into a single object. `script_data.*`:
    - `get_scene_ref_count` – get the number of scenes linking to the scene  
    - `get_button_ref_count` – get the number of buttons pointing to the scene  
    - `get_current_scene` – get the current scene data  
    - `get_current_scene_name` – get the current scene name  
    - `get_prev_scene` – get the previous scene data  
    - `get_prev_scene_name` – get the previous scene name
- Add new variables:
    - `scene_ref_count` – number of scenes linking to the current scene
    - `button_ref_count` – number of buttons pointing to the current scene
    - `prev_scene_name` – name of the previous scene
    - `prev_scene_title` – title of the previous scene
    - `prev_scene_message` – main text of the previous scene
- `TelekitDSL.Mixin` Refactoring:
    - Fixed the script data being prepared twice in `analyze_file`
    - New `ScriptData` class to group all script data

Happy New Year! 🎉