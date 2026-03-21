local key = KEYS[1]
local burst_capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local current_time = tonumber(ARGV[3])

local bucket_data = redis.call("GET", key)
local tokens = burst_capacity
local last_refill = current_time

if bucket_data then
    local state = cjson.decode(bucket_data)
    tokens = tonumber(state["tokens"])
    last_refill = tonumber(state["last_refill"])
end

local time_passed = current_time - last_refill
local tokens_to_add = time_passed * refill_rate
tokens = math.min(tokens + tokens_to_add, burst_capacity)

if tokens >= 1 then
    tokens = tokens - 1
    local new_state = cjson.encode({tokens = tokens, last_refill = current_time})
    redis.call("SET", key, new_state)
    return 1
else
    local new_state = cjson.encode({tokens = tokens, last_refill = last_refill})
    redis.call("SET", key, new_state)
    return 0
end
