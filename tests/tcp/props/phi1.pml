/* safety: half-open prevention */ 
ltl phi1 {
	always ( leftClosed implies !rightEstablished )
}
