class LLFFlux:
    def flux(Descr,U,n,dt):
        UL = U('-')
        UR = U('+')
        FL = Descr.F_c(UL)*n('+')
        FR = Descr.F_c(UR)*n('+')
        flux = (FL+FR)/2
        max_value = lambda a,b: (a+b+abs(a-b))/2.
        visc = max_value( Descr.alpha(UL,n('-')), Descr.alpha(UR,n('+')) )
        return flux + visc*(UR-UL)/2
NumFlux = LLFFlux.flux
