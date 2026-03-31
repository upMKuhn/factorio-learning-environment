util = require("util")

-- Pre-register ALL event handlers that RCON-injected scripts need.
-- This way the event handler table is stable from scenario load,
-- and joining peers see an identical script state.

script.on_event(defines.events.on_tick, function(event)
    -- Crafting queue processing (from utils.lua)
    if storage.crafting_queue then
        for i = #storage.crafting_queue, 1, -1 do
            local task = storage.crafting_queue[i]
            task.remaining_ticks = task.remaining_ticks - 1
            if task.remaining_ticks <= 0 then
                for _, ingredient in pairs(task.recipe.ingredients) do
                    task.player.remove_item({name = ingredient.name, count = ingredient.amount * task.count})
                end
                task.player.insert({name = task.entity_name, count = task.count})
                table.remove(storage.crafting_queue, i)
            end
        end
    end

    -- Alert checking (from alerts.lua) - every 60 ticks
    if event.tick % 60 == 0 and fle_utils and fle_utils.get_issues then
        for _, surface in pairs(game.surfaces) do
            local entities = surface.find_entities_filtered({force = "player"})
            for _, entity in pairs(entities) do
                local issues = fle_utils.get_issues(entity)
                if #issues > 0 then
                    local position = entity.position
                    local entity_key = entity.name .. "_" .. position.x .. "_" .. position.y
                    local name = '"'..entity.name:gsub(" ", "_")..'"'
                    if storage.alerts and not storage.alerts[entity_key] then
                        storage.alerts[entity_key] = {
                            position = position,
                            issues = issues,
                            entity_name = name,
                            tick = event.tick
                        }
                    end
                end
            end
        end
    end
end)

script.on_event(defines.events.on_script_path_request_finished, function(event)
    if not storage.path_requests then return end
    local request_data = storage.path_requests[event.id]
    if not request_data then return end

    if event.path then
        storage.paths[event.id] = event.path
    elseif event.try_again_later then
        storage.paths[event.id] = "busy"
    else
        storage.paths[event.id] = "not_found"
    end
end)

-- Walking queue updates (from move_to/server.lua) - every 5 ticks
script.on_nth_tick(5, function(event)
    if storage.walking_queues and fle_actions and fle_actions.update_walking_queues then
        fle_actions.update_walking_queues()
    end
end)

-- Harvest queue updates (from harvest_resource/server.lua) - every 15 ticks
script.on_nth_tick(15, function(event)
    if not storage.harvest_queues then return end
    if not fle_actions or not fle_actions.update_harvest_queues then return end
    fle_actions.update_harvest_queues(event)
end)

-- Slow placement / inventory inspection callbacks - every 60 ticks
script.on_nth_tick(60, function(event)
    if fle_actions and fle_actions.on_nth_tick_60 then
        fle_actions.on_nth_tick_60(event)
    end
end)
