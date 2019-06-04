(* --- *)
(* EXERCISE 1: GCD with lists *)

(* Question 1: product *)

let rec product = function
    [] -> 1
  | e::l -> e * product l;;

(* Question 2: decompose *)

let decompose u =
  if u <= 1 then 
    invalid_arg "decompose: parameter <= 1"
  else
    let rec decomp_rec q u =
      if u = 1 then
        []
      else 
	if u mod q = 0 then
          q :: decomp_rec q (u/q)
	else
          decomp_rec (q+1) u
    in
      decomp_rec 2 u ;;

(* Question 3: shared *)

let rec shared list1 list2 =
  match (list1, list2) with
    | ([],_) -> []
    | (_,[]) -> []
    | (e1::l1, e2::l2) -> 
                if e1 < e2 then 
            	   shared l1 (e2::l2)
                else 
                   if e2 < e1 then 
            	       shared (e1::l1) l2
                   else                        (* e1=e2 *)
            	       e1::shared l1 l2 ;;

(* Question 4: gcd *)

let gcd u v =
  product (shared (decompose u) (decompose v)) ;;


(* --- *)
(* EXERCISE 2: Decodable *)

(* Question 1: prefix *)

let rec prefix = function
    [], _ | _, [] -> true
  | e1::l1, e2::l2 -> if e1<>e2 then false else prefix (l1,l2);;

(* Question 2: is_prefix *)

let rec is_prefix list listlist =
  match listlist with
    [] -> false
  | l::ll -> prefix (l,list) || is_prefix list ll;;

(* Question 3: decodable *)

let decodable list = 
  if list = [] then 
    failwith "decodable: no codes!"
  else
    let rec dec = function
        [] -> true
      | e::l -> not(is_prefix e l) && dec l
    in
    dec list ;;


(* --- *)
(* EXERCISE 3: Long integers *)

(* Question 1: int_of_bigint *)

let rec int_of_bigint = function
    [] -> 0
  | e::l -> e + 10 * int_of_bigint l ;;


(* Question 2: bigint_of_int *)

let bigint_of_int n =
  if n < 0 then
    invalid_arg "longInt_of_int: not a natural"
  else
    let rec tolist n =
      if n = 0 then 
        [] 
      else
        (n mod 10) :: tolist (n / 10)
    in
      tolist n ;;


(* Question 2: bigint_sum *)

(* first version *)
  (* plus_one: add 1 to a longint *)

let plus_one = function 
    [] -> [1]
  | e::l -> (e+1)::l ;;

let rec bigint_sum big1 big2 =
  match (big1, big2) with
      ([], remain) | (remain, []) -> remain
    | (d1::r1, d2::r2) ->
        let s = d1 + d2 in
          if s < 10 then 
            s :: bigint_sum r1 r2
          else 
            (s - 10) :: bigint_sum (plus_one r1) r2 ;;

(* second version *)

let bigint_sum big1 big2 =
  let rec add = function
      ([], r) | (r, []) -> r
    | (d1::r1, d2::r2) ->
        let s = d1 + d2 in
          if s < 10 then 
            s :: add(r1, r2)
          else 
            (s - 10) :: add (add([1], r1), r2)
  in
    add (big1, big2) ;; 

(* Question 3: bigint_mult *)

let bigint_mult big n = 
  if n < 0 then
    invalid_arg "bigint_mult: negative multiplier"
  else
    let rec mult n = function
        ([], 0) -> []
      | ([], carry) -> bigint_of_int carry
      | (d::r, carry) -> let res = n * d + carry in
			 (res mod 10) :: mult n (r, res/10)
    in
    match n with
	0 -> []
      | 1 -> big
      | n -> mult n (big, 0) ;;

(* Question 4: bigint_times *)

let bigint_times big1 big2 = 
  let rec mult = function
      ([], _) | (_, []) -> []
    | (0::r, big) | (big, 0::r) -> 0::mult (r, big)
    | (1::[], big) | (big, 1::[]) -> big
    | (1::r, big) | (big, 1::r) -> bigint_sum big (0::mult (r, big))
    | (d::r, big) -> bigint_sum (bigint_mult big d) (0::mult (r, big))
  in 
    mult (big1, big2) ;;
