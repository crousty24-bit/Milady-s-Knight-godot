# Milady's Knight — Visual Asset Integration Rules

## Purpose

These instructions apply when Claude works on visual assets for Milady's Knight.

The primary role is not to redesign the game's visual identity.

The role is to analyze, select, adapt, normalize and integrate visual assets while preserving the project's existing Art Bible, gameplay requirements and technical constraints.

The active run always defines the permitted scope.

## Reference pipeline

Use the following pipeline when applicable:

source asset / asset pack  
→ inspection  
→ evaluation  
→ selection  
→ adaptation  
→ slicing / frame identification  
→ spritesheet preparation  
→ Godot import  
→ animation setup  
→ collision integration  
→ in-game verification

Not every run needs every stage.

Only execute the stages required by the active run.

## 1. Inspect before modifying

Before changing an asset:

- inspect the source files;
    
- inspect their dimensions;
    
- identify frame size and spritesheet organization;
    
- identify available animations;
    
- inspect naming and directory structure;
    
- check whether source files such as Aseprite or PSD are available;
    
- inspect existing related Godot scenes/resources;
    
- inspect how comparable assets are already integrated in the project.
    

Never infer a spritesheet structure without checking it.

Never assume an animation exists because it is expected by the game documentation.

## 2. Check project requirements

Evaluate assets against the relevant project documentation.

In particular verify:

- pixel-art compatibility;
    
- visual density;
    
- scale relative to the player and environment;
    
- animation availability;
    
- palette compatibility;
    
- silhouette readability;
    
- compatibility with the relevant biome;
    
- gameplay readability;
    
- technical suitability for Godot.
    

The current world reference grid is 16×16 px.

This does not mean every asset must be 16×16 px.

Asset dimensions may span multiple tiles, but their pixel density and world scale must remain visually coherent.

Do not rescale an incompatible asset merely because it can technically be resized.

## 3. Preserve source assets

Source assets must be preserved.

Do not destructively replace original files with normalized or edited variants.

Keep the conceptual separation between:

`assets/source/`

for original assets, references and source files,

and:

`assets/game/`

for normalized assets actually intended for use by Godot.

Do not delete apparently unused source assets unless their references and purpose have been verified.

## 4. Selection

When an asset pack contains multiple candidates, select only assets relevant to the active run.

Prefer assets that already satisfy the project constraints with minimal destructive adaptation.

Selection criteria include:

- native pixel art;
    
- side-scroller/platformer suitability;
    
- density close to the project reference;
    
- suitable character/world scale;
    
- regular and understandable spritesheets;
    
- required animations;
    
- compatible palette and outlines;
    
- modification rights;
    
- valid licensing for the project's intended use.
    

Do not integrate an entire asset pack solely because part of it is useful.

## 5. Adaptation

Adapt assets only when necessary.

Possible adaptation includes:

- cropping;
    
- frame extraction;
    
- spritesheet reconstruction;
    
- transparent-margin normalization;
    
- anchor alignment;
    
- limited palette harmonization;
    
- naming normalization;
    
- format conversion;
    
- organization into project directories.
    

Avoid unnecessary redraws or stylistic reinterpretation.

Do not change the gameplay meaning of an entity because its visual representation changes.

A visual variant may reuse an existing gameplay archetype without changing its behavior.

## 6. Spritesheets and animation frames

When preparing spritesheets:

- determine the real frame boundaries from the source;
    
- preserve consistent frame dimensions when appropriate;
    
- maintain a stable visual anchor across frames;
    
- avoid artificial movement caused by inconsistent alignment;
    
- retain enough canvas space for weapons, attacks or VFX when animations require it;
    
- do not crop animation content required by gameplay.
    

Do not assume the visible body dimensions equal the complete animation frame dimensions.

## 7. Godot import

Configure imported pixel-art assets according to the project rendering rules.

Preserve crisp pixel rendering.

Do not introduce filtering or arbitrary scaling that changes pixel density.

Before changing existing import configuration, inspect the current project settings and existing comparable assets.

Reuse established project patterns when they are valid.

## 8. Animations

Only create animations required by the relevant entity and active run.

Possible animation categories include:

- idle;
    
- move / walk;
    
- attack;
    
- hit / damage;
    
- death;
    
- special abilities;
    
- environmental loops;
    
- interaction animations.
    

Animation names and structure should follow existing project conventions when such conventions already exist.

Do not invent missing gameplay states merely to use animations provided by an asset pack.

## 9. Collisions

Collision shapes are gameplay components, not direct copies of sprite bounds.

Define or adjust collisions according to the intended gameplay behavior.

Do not automatically create a collision matching every visible pixel.

For character assets, evaluate independently:

- body collision;
    
- hitbox;
    
- hurtbox;
    
- attack area;
    
- interaction area;
    
- projectile collision;
    

when relevant to the active run and existing architecture.

Changes to collision behavior must be tested.

## 10. Visual readability

Gameplay readability has priority over decorative fidelity.

Verify that:

- the player remains clearly identifiable;
    
- enemies remain distinguishable from terrain and backgrounds;
    
- interactable objects remain identifiable;
    
- traps remain readable;
    
- projectiles remain visible;
    
- VFX do not hide important gameplay information.
    

Do not solve dark-fantasy atmosphere by making gameplay elements unreadably dark.

## 11. Scale validation

Check assets in actual gameplay context rather than evaluating them only as standalone images.

When relevant, compare against:

- player scale;
    
- terrain tiles;
    
- standard enemies;
    
- large enemies;
    
- traps;
    
- doors;
    
- chests;
    
- nearby environment elements.
    

Do not adopt an asset pack globally after inspecting only its preview images.

Prefer validating a limited representative sample first.

## 12. Licensing and provenance

For every third-party asset integrated into the project, preserve relevant provenance information:

- source;
    
- author;
    
- license;
    
- attribution requirements;
    
- modification rights;
    
- commercial-use rights where applicable;
    
- AI-related conditions where applicable.
    

Do not remove existing license or attribution information.

If licensing information cannot be verified, do not present the asset as cleared for integration.

## 13. Testing

Visual integration is not complete when the file merely imports successfully.

When applicable, verify:

- correct dimensions;
    
- correct scale;
    
- correct frame slicing;
    
- animation playback;
    
- anchor stability;
    
- texture filtering;
    
- collision alignment;
    
- visual readability;
    
- interaction with terrain;
    
- interaction with the player;
    
- relevant combat behavior;
    
- obvious regressions.
    

Use a representative gameplay context whenever possible.

For early asset validation, prefer testing a limited sample before integrating an entire pack.

## 14. Human validation

Some visual judgments cannot be treated as objectively validated by automated inspection alone.

When relevant, leave final human validation for:

- artistic fit;
    
- animation feel;
    
- readability during real gameplay;
    
- perceived scale;
    
- collision feel;
    
- visual consistency with surrounding assets.
    

Do not claim subjective visual approval on behalf of the user.

## 15. Completion rule

An asset integration task is complete only when the required pipeline stages defined by the active run have been executed and verified.

A successfully imported PNG is not, by itself, a completed asset integration.