v3 failures: doc_id,field,expected,got
017.jpg,subtotal,,58.42
029.jpg,subtotal,,49.99
055.pdf,total,46.31,

v4, cheaper model, failures: doc_id,field,expected,got
001.pdf,date,2026-10-03,
005.jpg,vendor,green basket market,
005.jpg,date,2026-10-14,
005.jpg,subtotal,34.14,
005.jpg,tax,0.0,
005.jpg,total,34.14,
005.jpg,currency,usd,
019.jpg,vendor,olive ember,
019.jpg,date,2026-07-11,
019.jpg,subtotal,57.7,
019.jpg,tax,4.18,
019.jpg,total,73.42,
019.jpg,currency,usd,
029.jpg,subtotal,,49.99
046.jpg,date,2026-08-06,
050.jpg,vendor,morning fog coffee,
050.jpg,date,2026-03-04,
050.jpg,subtotal,5.25,
050.jpg,tax,0.46,
050.jpg,total,5.71,
050.jpg,currency,usd,
053.jpg,vendor,freshway foods 214,freshway foods
055.pdf,total,46.31,

v5, stronger model, failures: doc_id,field,expected,got
001.pdf,date,2026-10-03,
021.jpg,date,2026-09-04,
029.jpg,subtotal,,49.99
050.jpg,date,2026-03-04,
052.jpg,subtotal,,60.0
055.pdf,total,46.31,
058.pdf,date,2026-08-04,

v6, better labeling, failures: doc_id,field,expected,got
055.pdf,total,46.31,

v7, better labeling, cheaper model, failures: doc_id,field,expected,got
005.jpg,subtotal,34.14,0.0
012.jpg,currency,usd,
019.jpg,vendor,olive ember,
019.jpg,date,2026-07-11,
019.jpg,subtotal,57.7,
019.jpg,tax,4.18,
019.jpg,total,73.42,
019.jpg,currency,usd,

v8 was perfect, sonnet with labeling, one label was fixed

“v9 checks: X of 60 flagged, 0 real errors (all false alarms), 0 missed errors.”