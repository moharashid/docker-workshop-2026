---

## Question 3
**For the trips in November 2025, how many trips had a trip_distance of less than or equal to 1 mile?**

```sql
SELECT COUNT(trip_distance)
FROM public.green_taxi_trips_nov_2025
WHERE trip_distance <= 1
  AND lpep_pickup_datetime BETWEEN '2025-11-01' AND '2025-12-01';
```
## Question 4
**Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles. (1 point)**

```sql
SELECT date_trunc('day', lpep_pickup_datetime) AS pickup_day,
       trip_distance
FROM public.green_taxi_trips_nov_2025
WHERE trip_distance <= 100
ORDER BY trip_distance DESC
LIMIT 1;
```

## Question 5
**Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles. (1 point)**

```sql
SELECT SUM(g.total_amount) AS total_amount,
       l."Borough",
       l."Zone",
       date_trunc('day', g.lpep_pickup_datetime) AS d
FROM public.green_taxi_trips_nov_2025 g
JOIN public.taxi_lookup l
  ON g."PULocationID" = l."LocationID"
WHERE date_trunc('day', g.lpep_pickup_datetime) = DATE '2025-11-18'
GROUP BY l."Borough", l."Zone", d
ORDER BY total_amount DESC
LIMIT 5;
```

## Question 6
**Which was the pick up day with the longest trip distance? Only consider trips with trip_distance less than 100 miles. (1 point)**

```sql
SELECT
  do_l."Borough" AS dropoff_borough,
  do_l."Zone"    AS dropoff_zone,
  g.tip_amount
FROM public.green_taxi_trips_nov_2025 g
JOIN public.taxi_lookup pu
  ON g."PULocationID" = pu."LocationID"
JOIN public.taxi_lookup do_l
  ON g."DOLocationID" = do_l."LocationID"
WHERE pu."Zone" = 'East Harlem North'
  AND g.lpep_pickup_datetime >= '2025-11-01'
  AND g.lpep_pickup_datetime <  '2025-12-01'
ORDER BY g.tip_amount DESC
LIMIT 1;
```
