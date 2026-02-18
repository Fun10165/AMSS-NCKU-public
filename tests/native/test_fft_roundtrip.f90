program test_fft_roundtrip
  implicit none
  integer, parameter :: n = 16
  integer :: i
  double precision :: maxerr
  double precision, dimension(2*n) :: data, original

  external :: four1

  do i = 1, n
    data(2*i-1) = dble(i) / dble(n)
    data(2*i)   = dble(mod(i, 3)) - 1.0d0
  end do

  original = data

  call four1(data, n, 1)
  call four1(data, n, -1)

  maxerr = 0.0d0
  do i = 1, 2*n
    maxerr = max(maxerr, abs(data(i) - dble(n) * original(i)))
  end do

  ! The AMSS FFT implementation uses intermediate `sngl(...)` casts,
  ! so roundtrip errors around 1e-6 can occur across compiler versions.
  if (maxerr > 5.0d-6) then
    print *, "FFT roundtrip failed, maxerr =", maxerr
    stop 1
  end if

  print *, "Fortran FFT test passed, maxerr =", maxerr
end program test_fft_roundtrip
