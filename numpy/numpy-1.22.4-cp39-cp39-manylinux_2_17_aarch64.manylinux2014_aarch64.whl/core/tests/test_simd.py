# NOTE: Please avoid the use of numpy.testing since NPYV intrinsics
# may be involved in their functionality.
import pytest, math, re
import itertools
from numpy.core._simd import targets
from numpy.core._multiarray_umath import __cpu_baseline__

class _Test_Utility:
    # submodule of the desired SIMD extension, e.g. targets["AVX512F"]
    npyv = None
    # the current data type suffix e.g. 's8'
    sfx  = None
    # target name can be 'baseline' or one or more of CPU features
    target_name = None

    def __getattr__(self, attr):
        """
        To call NPV intrinsics without the attribute 'npyv' and
        auto suffixing intrinsics according to class attribute 'sfx'
        """
        return getattr(self.npyv, attr + "_" + self.sfx)

    def _data(self, start=None, count=None, reverse=False):
        """
        Create list of consecutive numbers according to number of vector's lanes.
        """
        if start is None:
            start = 1
        if count is None:
            count = self.nlanes
        rng = range(start, start + count)
        if reverse:
            rng = reversed(rng)
        if self._is_fp():
            return [x / 1.0 for x in rng]
        return list(rng)

    def _is_unsigned(self):
        return self.sfx[0] == 'u'

    def _is_signed(self):
        return self.sfx[0] == 's'

    def _is_fp(self):
        return self.sfx[0] == 'f'

    def _scalar_size(self):
        return int(self.sfx[1:])

    def _int_clip(self, seq):
        if self._is_fp():
            return seq
        max_int = self._int_max()
        min_int = self._int_min()
        return [min(max(v, min_int), max_int) for v in seq]

    def _int_max(self):
        if self._is_fp():
            return None
        max_u = self._to_unsigned(self.setall(-1))[0]
        if self._is_signed():
            return max_u // 2
        return max_u

    def _int_min(self):
        if self._is_fp():
            return None
        if self._is_unsigned():
            return 0
        return -(self._int_max() + 1)

    def _true_mask(self):
        max_unsig = getattr(self.npyv, "setall_u" + self.sfx[1:])(-1)
        return max_unsig[0]

    def _to_unsigned(self, vector):
        if isinstance(vector, (list, tuple)):
            return getattr(self.npyv, "load_u" + self.sfx[1:])(vector)
        else:
            sfx = vector.__name__.replace("npyv_", "")
            if sfx[0] == "b":
                cvt_intrin = "cvt_u{0}_b{0}"
            else:
                cvt_intrin = "reinterpret_u{0}_{1}"
            return getattr(self.npyv, cvt_intrin.format(sfx[1:], sfx))(vector)

    def _pinfinity(self):
        v = self.npyv.setall_u32(0x7f800000)
        return self.npyv.reinterpret_f32_u32(v)[0]

    def _ninfinity(self):
        v = self.npyv.setall_u32(0xff800000)
        return self.npyv.reinterpret_f32_u32(v)[0]

    def _nan(self):
        v = self.npyv.setall_u32(0x7fc00000)
        return self.npyv.reinterpret_f32_u32(v)[0]

    def _cpu_features(self):
        target = self.target_name
        if target == "baseline":
            target = __cpu_baseline__
        else:
            target = target.split('__') # multi-target separator
        return ' '.join(target)

class _SIMD_BOOL(_Test_Utility):
    """
    To test all boolean vector types at once
    """
    def _data(self, start=None, count=None, reverse=False):
        nlanes = getattr(self.npyv, "nlanes_u" + self.sfx[1:])
        true_mask = self._true_mask()
        rng = range(nlanes)
        if reverse:
            rng = reversed(rng)
        return [true_mask if x % 2 else 0 for x in rng]

    def _load_b(self, data):
        len_str = self.sfx[1:]
        load = getattr(self.npyv, "load_u" + len_str)
        cvt = getattr(self.npyv, f"cvt_b{len_str}_u{len_str}")
        return cvt(load(data))

    def test_operators_logical(self):
        """
        Logical operations for boolean types.
        Test intrinsics:
            npyv_xor_##SFX, npyv_and_##SFX, npyv_or_##SFX, npyv_not_##SFX
        """
        data_a = self._data()
        data_b = self._data(reverse=True)
        vdata_a = self._load_b(data_a)
        vdata_b = self._load_b(data_b)

        data_and = [a & b for a, b in zip(data_a, data_b)]
        vand = getattr(self, "and")(vdata_a, vdata_b)
        assert vand == data_and

        data_or = [a | b for a, b in zip(data_a, data_b)]
        vor = getattr(self, "or")(vdata_a, vdata_b)
        assert vor == data_or

        data_xor = [a ^ b for a, b in zip(data_a, data_b)]
        vxor = getattr(self, "xor")(vdata_a, vdata_b)
        assert vxor == data_xor

        vnot = getattr(self, "not")(vdata_a)
        assert vnot == data_b

    def test_tobits(self):
        data2bits = lambda data: sum([int(x != 0) << i for i, x in enumerate(data, 0)])
        for data in (self._data(), self._data(reverse=True)):
            vdata = self._load_b(data)
            data_bits = data2bits(data)
            tobits = bin(self.tobits(vdata))
            assert tobits == bin(data_bits)

class _SIMD_INT(_Test_Utility):
    """
    To test all integer vector types at once
    """
    def test_operators_shift(self):
        if self.sfx in ("u8", "s8"):
            return

        data_a = self._data(self._int_max() - self.nlanes)
        data_b = self._data(self._int_min(), reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        for count in range(self._scalar_size()):
            # load to cast
            data_shl_a = self.load([a << count for a in data_a])
            # left shift
            shl = self.shl(vdata_a, count)
            assert shl == data_shl_a
            # load to cast
            data_shr_a = self.load([a >> count for a in data_a])
            # right shift
            shr = self.shr(vdata_a, count)
            assert shr == data_shr_a

        # shift by zero or max or out-range immediate constant is not applicable and illogical
        for count in range(1, self._scalar_size()):
            # load to cast
            data_shl_a = self.load([a << count for a in data_a])
            # left shift by an immediate constant
            shli = self.shli(vdata_a, count)
            assert shli == data_shl_a
            # load to cast
            data_shr_a = self.load([a >> count for a in data_a])
            # right shift by an immediate constant
            shri = self.shri(vdata_a, count)
            assert shri == data_shr_a

    def test_arithmetic_subadd_saturated(self):
        if self.sfx in ("u32", "s32", "u64", "s64"):
            return

        data_a = self._data(self._int_max() - self.nlanes)
        data_b = self._data(self._int_min(), reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        data_adds = self._int_clip([a + b for a, b in zip(data_a, data_b)])
        adds = self.adds(vdata_a, vdata_b)
        assert adds == data_adds

        data_subs = self._int_clip([a - b for a, b in zip(data_a, data_b)])
        subs = self.subs(vdata_a, vdata_b)
        assert subs == data_subs

    def test_math_max_min(self):
        data_a = self._data()
        data_b = self._data(self.nlanes)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        data_max = [max(a, b) for a, b in zip(data_a, data_b)]
        simd_max = self.max(vdata_a, vdata_b)
        assert simd_max == data_max

        data_min = [min(a, b) for a, b in zip(data_a, data_b)]
        simd_min = self.min(vdata_a, vdata_b)
        assert simd_min == data_min

class _SIMD_FP32(_Test_Utility):
    """
    To only test single precision
    """
    def test_conversions(self):
        """
        Round to nearest even integer, assume CPU control register is set to rounding.
        Test intrinsics:
            npyv_round_s32_##SFX
        """
        features = self._cpu_features()
        if not self.npyv.simd_f64 and re.match(r".*(NEON|ASIMD)", features):
            # very costly to emulate nearest even on Armv7
            # instead we round halves to up. e.g. 0.5 -> 1, -0.5 -> -1
            _round = lambda v: int(v + (0.5 if v >= 0 else -0.5))
        else:
            _round = round
        vdata_a = self.load(self._data())
        vdata_a = self.sub(vdata_a, self.setall(0.5))
        data_round = [_round(x) for x in vdata_a]
        vround = self.round_s32(vdata_a)
        assert vround == data_round

class _SIMD_FP64(_Test_Utility):
    """
    To only test double precision
    """
    def test_conversions(self):
        """
        Round to nearest even integer, assume CPU control register is set to rounding.
        Test intrinsics:
            npyv_round_s32_##SFX
        """
        vdata_a = self.load(self._data())
        vdata_a = self.sub(vdata_a, self.setall(0.5))
        vdata_b = self.mul(vdata_a, self.setall(-1.5))
        data_round = [round(x) for x in list(vdata_a) + list(vdata_b)]
        vround = self.round_s32(vdata_a, vdata_b)
        assert vround == data_round

class _SIMD_FP(_Test_Utility):
    """
    To test all float vector types at once
    """
    def test_arithmetic_fused(self):
        vdata_a, vdata_b, vdata_c = [self.load(self._data())]*3
        vdata_cx2 = self.add(vdata_c, vdata_c)
        # multiply and add, a*b + c
        data_fma = self.load([a * b + c for a, b, c in zip(vdata_a, vdata_b, vdata_c)])
        fma = self.muladd(vdata_a, vdata_b, vdata_c)
        assert fma == data_fma
        # multiply and subtract, a*b - c
        fms = self.mulsub(vdata_a, vdata_b, vdata_c)
        data_fms = self.sub(data_fma, vdata_cx2)
        assert fms == data_fms
        # negate multiply and add, -(a*b) + c
        nfma = self.nmuladd(vdata_a, vdata_b, vdata_c)
        data_nfma = self.sub(vdata_cx2, data_fma)
        assert nfma == data_nfma
        # negate multiply and subtract, -(a*b) - c
        nfms = self.nmulsub(vdata_a, vdata_b, vdata_c)
        data_nfms = self.mul(data_fma, self.setall(-1))
        assert nfms == data_nfms

    def test_abs(self):
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        data = self._data()
        vdata = self.load(self._data())

        abs_cases = ((-0, 0), (ninf, pinf), (pinf, pinf), (nan, nan))
        for case, desired in abs_cases:
            data_abs = [desired]*self.nlanes
            vabs = self.abs(self.setall(case))
            assert vabs == pytest.approx(data_abs, nan_ok=True)

        vabs = self.abs(self.mul(vdata, self.setall(-1)))
        assert vabs == data

    def test_sqrt(self):
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        data = self._data()
        vdata = self.load(self._data())

        sqrt_cases = ((-0.0, -0.0), (0.0, 0.0), (-1.0, nan), (ninf, nan), (pinf, pinf))
        for case, desired in sqrt_cases:
            data_sqrt = [desired]*self.nlanes
            sqrt  = self.sqrt(self.setall(case))
            assert sqrt == pytest.approx(data_sqrt, nan_ok=True)

        data_sqrt = self.load([math.sqrt(x) for x in data]) # load to truncate precision
        sqrt = self.sqrt(vdata)
        assert sqrt == data_sqrt

    def test_square(self):
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        data = self._data()
        vdata = self.load(self._data())
        # square
        square_cases = ((nan, nan), (pinf, pinf), (ninf, pinf))
        for case, desired in square_cases:
            data_square = [desired]*self.nlanes
            square  = self.square(self.setall(case))
            assert square == pytest.approx(data_square, nan_ok=True)

        data_square = [x*x for x in data]
        square = self.square(vdata)
        assert square == data_square

    @pytest.mark.parametrize("intrin, func", [("self.ceil", math.ceil),
    ("self.trunc", math.trunc)])
    def test_rounding(self, intrin, func):
        """
        Test intrinsics:
            npyv_ceil_##SFX
            npyv_trunc_##SFX
        """
        intrin_name = intrin
        intrin = eval(intrin)
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        # special cases
        round_cases = ((nan, nan), (pinf, pinf), (ninf, ninf))
        for case, desired in round_cases:
            data_round = [desired]*self.nlanes
            _round = intrin(self.setall(case))
            assert _round == pytest.approx(data_round, nan_ok=True)
        for x in range(0, 2**20, 256**2):
            for w in (-1.05, -1.10, -1.15, 1.05, 1.10, 1.15):
                data = [x*w+a for a in range(self.nlanes)]
                vdata = self.load(data)
                data_round = [func(x) for x in data]
                _round = intrin(vdata)
                assert _round == data_round
        # signed zero
        if "ceil" in intrin_name or "trunc" in intrin_name:
            for w in (-0.25, -0.30, -0.45):
                _round = self._to_unsigned(intrin(self.setall(w)))
                data_round = self._to_unsigned(self.setall(-0.0))
                assert _round == data_round
    
    def test_max(self):
        """
        Test intrinsics:
            npyv_max_##SFX
            npyv_maxp_##SFX
        """
        data_a = self._data()
        data_b = self._data(self.nlanes)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)
        data_max = [max(a, b) for a, b in zip(data_a, data_b)]
        _max = self.max(vdata_a, vdata_b)
        assert _max == data_max
        maxp = self.maxp(vdata_a, vdata_b)
        assert maxp == data_max
        # test IEEE standards
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        max_cases = ((nan, nan, nan), (nan, 10, 10), (10, nan, 10),
                     (pinf, pinf, pinf), (pinf, 10, pinf), (10, pinf, pinf),
                     (ninf, ninf, ninf), (ninf, 10, 10), (10, ninf, 10),
                     (10, 0, 10), (10, -10, 10))
        for case_operand1, case_operand2, desired in max_cases:
            data_max = [desired]*self.nlanes
            vdata_a = self.setall(case_operand1)
            vdata_b = self.setall(case_operand2)
            maxp = self.maxp(vdata_a, vdata_b)
            assert maxp == pytest.approx(data_max, nan_ok=True)
            if nan in (case_operand1, case_operand2, desired):
                continue
            _max = self.max(vdata_a, vdata_b)
            assert _max == data_max

    def test_min(self):
        """
        Test intrinsics:
            npyv_min_##SFX
            npyv_minp_##SFX
        """
        data_a = self._data()
        data_b = self._data(self.nlanes)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)
        data_min = [min(a, b) for a, b in zip(data_a, data_b)]
        _min = self.min(vdata_a, vdata_b)
        assert _min == data_min
        minp = self.minp(vdata_a, vdata_b)
        assert minp == data_min
        # test IEEE standards
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        min_cases = ((nan, nan, nan), (nan, 10, 10), (10, nan, 10),
                     (pinf, pinf, pinf), (pinf, 10, 10), (10, pinf, 10),
                     (ninf, ninf, ninf), (ninf, 10, ninf), (10, ninf, ninf),
                     (10, 0, 0), (10, -10, -10))
        for case_operand1, case_operand2, desired in min_cases:
            data_min = [desired]*self.nlanes
            vdata_a = self.setall(case_operand1)
            vdata_b = self.setall(case_operand2)
            minp = self.minp(vdata_a, vdata_b)
            assert minp == pytest.approx(data_min, nan_ok=True)
            if nan in (case_operand1, case_operand2, desired):
                continue
            _min = self.min(vdata_a, vdata_b)
            assert _min == data_min

    def test_reciprocal(self):
        pinf, ninf, nan = self._pinfinity(), self._ninfinity(), self._nan()
        data = self._data()
        vdata = self.load(self._data())

        recip_cases = ((nan, nan), (pinf, 0.0), (ninf, -0.0), (0.0, pinf), (-0.0, ninf))
        for case, desired in recip_cases:
            data_recip = [desired]*self.nlanes
            recip = self.recip(self.setall(case))
            assert recip == pytest.approx(data_recip, nan_ok=True)

        data_recip = self.load([1/x for x in data]) # load to truncate precision
        recip = self.recip(vdata)
        assert recip == data_recip

    def test_special_cases(self):
        """
        Compare Not NaN. Test intrinsics:
            npyv_notnan_##SFX
        """
        nnan = self.notnan(self.setall(self._nan()))
        assert nnan == [0]*self.nlanes

class _SIMD_ALL(_Test_Utility):
    """
    To test all vector types at once
    """
    def test_memory_load(self):
        data = self._data()
        # unaligned load
        load_data = self.load(data)
        assert load_data == data
        # aligned load
        loada_data = self.loada(data)
        assert loada_data == data
        # stream load
        loads_data = self.loads(data)
        assert loads_data == data
        # load lower part
        loadl = self.loadl(data)
        loadl_half = list(loadl)[:self.nlanes//2]
        data_half = data[:self.nlanes//2]
        assert loadl_half == data_half
        assert loadl != data # detect overflow

    def test_memory_store(self):
        data = self._data()
        vdata = self.load(data)
        # unaligned store
        store = [0] * self.nlanes
        self.store(store, vdata)
        assert store == data
        # aligned store
        store_a = [0] * self.nlanes
        self.storea(store_a, vdata)
        assert store_a == data
        # stream store
        store_s = [0] * self.nlanes
        self.stores(store_s, vdata)
        assert store_s == data
        # store lower part
        store_l = [0] * self.nlanes
        self.storel(store_l, vdata)
        assert store_l[:self.nlanes//2] == data[:self.nlanes//2]
        assert store_l != vdata # detect overflow
        # store higher part
        store_h = [0] * self.nlanes
        self.storeh(store_h, vdata)
        assert store_h[:self.nlanes//2] == data[self.nlanes//2:]
        assert store_h != vdata  # detect overflow

    def test_memory_partial_load(self):
        if self.sfx in ("u8", "s8", "u16", "s16"):
            return

        data = self._data()
        lanes = list(range(1, self.nlanes + 1))
        lanes += [self.nlanes**2, self.nlanes**4] # test out of range
        for n in lanes:
            load_till  = self.load_till(data, n, 15)
            data_till  = data[:n] + [15] * (self.nlanes-n)
            assert load_till == data_till
            load_tillz = self.load_tillz(data, n)
            data_tillz = data[:n] + [0] * (self.nlanes-n)
            assert load_tillz == data_tillz

    def test_memory_partial_store(self):
        if self.sfx in ("u8", "s8", "u16", "s16"):
            return

        data = self._data()
        data_rev = self._data(reverse=True)
        vdata = self.load(data)
        lanes = list(range(1, self.nlanes + 1))
        lanes += [self.nlanes**2, self.nlanes**4]
        for n in lanes:
            data_till = data_rev.copy()
            data_till[:n] = data[:n]
            store_till = self._data(reverse=True)
            self.store_till(store_till, n, vdata)
            assert store_till == data_till

    def test_memory_noncont_load(self):
        if self.sfx in ("u8", "s8", "u16", "s16"):
            return

        for stride in range(1, 64):
            data = self._data(count=stride*self.nlanes)
            data_stride = data[::stride]
            loadn = self.loadn(data, stride)
            assert loadn == data_stride

        for stride in range(-64, 0):
            data = self._data(stride, -stride*self.nlanes)
            data_stride = self.load(data[::stride]) # cast unsigned
            loadn = self.loadn(data, stride)
            assert loadn == data_stride

    def test_memory_noncont_partial_load(self):
        if self.sfx in ("u8", "s8", "u16", "s16"):
            return

        lanes = list(range(1, self.nlanes + 1))
        lanes += [self.nlanes**2, self.nlanes**4]
        for stride in range(1, 64):
            data = self._data(count=stride*self.nlanes)
            data_stride = data[::stride]
            for n in lanes:
                data_stride_till = data_stride[:n] + [15] * (self.nlanes-n)
                loadn_till = self.loadn_till(data, stride, n, 15)
                assert loadn_till == data_stride_till
                data_stride_tillz = data_stride[:n] + [0] * (self.nlanes-n)
                loadn_tillz = self.loadn_tillz(data, stride, n)
                assert loadn_tillz == data_stride_tillz

        for stride in range(-64, 0):
            data = self._data(stride, -stride*self.nlanes)
            data_stride = list(self.load(data[::stride])) # cast unsigned
            for n in lanes:
                data_stride_till = data_stride[:n] + [15] * (self.nlanes-n)
                loadn_till = self.loadn_till(data, stride, n, 15)
                assert loadn_till == data_stride_till
                data_stride_tillz = data_stride[:n] + [0] * (self.nlanes-n)
                loadn_tillz = self.loadn_tillz(data, stride, n)
                assert loadn_tillz == data_stride_tillz

    def test_memory_noncont_store(self):
        if self.sfx in ("u8", "s8", "u16", "s16"):
            return

        vdata = self.load(self._data())
        for stride in range(1, 64):
            data = [15] * stride * self.nlanes
            data[::stride] = vdata
            storen = [15] * stride * self.nlanes
            storen += [127]*64
            self.storen(storen, stride, vdata)
            assert storen[:-64] == data
            assert storen[-64:] == [127]*64 # detect overflow

        for stride in range(-64, 0):
            data = [15] * -stride * self.nlanes
            data[::stride] = vdata
            storen = [127]*64
            storen += [15] * -stride * self.nlanes
            self.storen(storen, stride, vdata)
            assert storen[64:] == data
            assert storen[:64] == [127]*64 # detect overflow

    def test_memory_noncont_partial_store(self):
        if self.sfx in ("u8", "s8", "u16", "s16"):
            return

        data = self._data()
        vdata = self.load(data)
        lanes = list(range(1, self.nlanes + 1))
        lanes += [self.nlanes**2, self.nlanes**4]
        for stride in range(1, 64):
            for n in lanes:
                data_till = [15] * stride * self.nlanes
                data_till[::stride] = data[:n] + [15] * (self.nlanes-n)
                storen_till = [15] * stride * self.nlanes
                storen_till += [127]*64
                self.storen_till(storen_till, stride, n, vdata)
                assert storen_till[:-64] == data_till
                assert storen_till[-64:] == [127]*64 # detect overflow

        for stride in range(-64, 0):
            for n in lanes:
                data_till = [15] * -stride * self.nlanes
                data_till[::stride] = data[:n] + [15] * (self.nlanes-n)
                storen_till = [127]*64
                storen_till += [15] * -stride * self.nlanes
                self.storen_till(storen_till, stride, n, vdata)
                assert storen_till[64:] == data_till
                assert storen_till[:64] == [127]*64 # detect overflow

    def test_misc(self):
        broadcast_zero = self.zero()
        assert broadcast_zero == [0] * self.nlanes
        for i in range(1, 10):
            broadcasti = self.setall(i)
            assert broadcasti == [i] * self.nlanes

        data_a, data_b = self._data(), self._data(reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        # py level of npyv_set_* don't support ignoring the extra specified lanes or
        # fill non-specified lanes with zero.
        vset = self.set(*data_a)
        assert vset == data_a
        # py level of npyv_setf_* don't support ignoring the extra specified lanes or
        # fill non-specified lanes with the specified scalar.
        vsetf = self.setf(10, *data_a)
        assert vsetf == data_a

        # We're testing the sanity of _simd's type-vector,
        # reinterpret* intrinsics itself are tested via compiler
        # during the build of _simd module
        sfxes = ["u8", "s8", "u16", "s16", "u32", "s32", "u64", "s64", "f32"]
        if self.npyv.simd_f64:
            sfxes.append("f64")
        for sfx in sfxes:
            vec_name = getattr(self, "reinterpret_" + sfx)(vdata_a).__name__
            assert vec_name == "npyv_" + sfx

        # select & mask operations
        select_a = self.select(self.cmpeq(self.zero(), self.zero()), vdata_a, vdata_b)
        assert select_a == data_a
        select_b = self.select(self.cmpneq(self.zero(), self.zero()), vdata_a, vdata_b)
        assert select_b == data_b

        # cleanup intrinsic is only used with AVX for
        # zeroing registers to avoid the AVX-SSE transition penalty,
        # so nothing to test here
        self.npyv.cleanup()

    def test_reorder(self):
        data_a, data_b  = self._data(), self._data(reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)
        # lower half part
        data_a_lo = data_a[:self.nlanes//2]
        data_b_lo = data_b[:self.nlanes//2]
        # higher half part
        data_a_hi = data_a[self.nlanes//2:]
        data_b_hi = data_b[self.nlanes//2:]
        # combine two lower parts
        combinel = self.combinel(vdata_a, vdata_b)
        assert combinel == data_a_lo + data_b_lo
        # combine two higher parts
        combineh = self.combineh(vdata_a, vdata_b)
        assert combineh == data_a_hi + data_b_hi
        # combine x2
        combine  = self.combine(vdata_a, vdata_b)
        assert combine == (data_a_lo + data_b_lo, data_a_hi + data_b_hi)
        # zip(interleave)
        data_zipl = [v for p in zip(data_a_lo, data_b_lo) for v in p]
        data_ziph = [v for p in zip(data_a_hi, data_b_hi) for v in p]
        vzip  = self.zip(vdata_a, vdata_b)
        assert vzip == (data_zipl, data_ziph)

    def test_reorder_rev64(self):
        # Reverse elements of each 64-bit lane
        ssize = self._scalar_size()
        if ssize == 64:
            return
        data_rev64 = [
            y for x in range(0, self.nlanes, 64//ssize)
              for y in reversed(range(x, x + 64//ssize))
        ]
        rev64 = self.rev64(self.load(range(self.nlanes)))
        assert rev64 == data_rev64

    def test_operators_comparison(self):
        if self._is_fp():
            data_a = self._data()
        else:
            data_a = self._data(self._int_max() - self.nlanes)
        data_b = self._data(self._int_min(), reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        mask_true = self._true_mask()
        def to_bool(vector):
            return [lane == mask_true for lane in vector]
        # equal
        data_eq = [a == b for a, b in zip(data_a, data_b)]
        cmpeq = to_bool(self.cmpeq(vdata_a, vdata_b))
        assert cmpeq == data_eq
        # not equal
        data_neq = [a != b for a, b in zip(data_a, data_b)]
        cmpneq = to_bool(self.cmpneq(vdata_a, vdata_b))
        assert cmpneq == data_neq
        # greater than
        data_gt = [a > b for a, b in zip(data_a, data_b)]
        cmpgt = to_bool(self.cmpgt(vdata_a, vdata_b))
        assert cmpgt == data_gt
        # greater than and equal
        data_ge = [a >= b for a, b in zip(data_a, data_b)]
        cmpge = to_bool(self.cmpge(vdata_a, vdata_b))
        assert cmpge == data_ge
        # less than
        data_lt  = [a < b for a, b in zip(data_a, data_b)]
        cmplt = to_bool(self.cmplt(vdata_a, vdata_b))
        assert cmplt == data_lt
        # less than and equal
        data_le  = [a <= b for a, b in zip(data_a, data_b)]
        cmple = to_bool(self.cmple(vdata_a, vdata_b))
        assert cmple == data_le

    def test_operators_logical(self):
        if self._is_fp():
            data_a = self._data()
        else:
            data_a = self._data(self._int_max() - self.nlanes)
        data_b = self._data(self._int_min(), reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        if self._is_fp():
            data_cast_a = self._to_unsigned(vdata_a)
            data_cast_b = self._to_unsigned(vdata_b)
            cast, cast_data = self._to_unsigned, self._to_unsigned
        else:
            data_cast_a, data_cast_b = data_a, data_b
            cast, cast_data = lambda a: a, self.load

        data_xor = cast_data([a ^ b for a, b in zip(data_cast_a, data_cast_b)])
        vxor = cast(self.xor(vdata_a, vdata_b))
        assert vxor == data_xor

        data_or  = cast_data([a | b for a, b in zip(data_cast_a, data_cast_b)])
        vor  = cast(getattr(self, "or")(vdata_a, vdata_b))
        assert vor == data_or

        data_and = cast_data([a & b for a, b in zip(data_cast_a, data_cast_b)])
        vand = cast(getattr(self, "and")(vdata_a, vdata_b))
        assert vand == data_and

        data_not = cast_data([~a for a in data_cast_a])
        vnot = cast(getattr(self, "not")(vdata_a))
        assert vnot == data_not

    def test_conversion_boolean(self):
        bsfx = "b" + self.sfx[1:]
        to_boolean = getattr(self.npyv, "cvt_%s_%s" % (bsfx, self.sfx))
        from_boolean = getattr(self.npyv, "cvt_%s_%s" % (self.sfx, bsfx))

        false_vb = to_boolean(self.setall(0))
        true_vb  = self.cmpeq(self.setall(0), self.setall(0))
        assert false_vb != true_vb

        false_vsfx = from_boolean(false_vb)
        true_vsfx = from_boolean(true_vb)
        assert false_vsfx != true_vsfx

    def test_conversion_expand(self):
        """
        Test expand intrinsics:
            npyv_expand_u16_u8
            npyv_expand_u32_u16
        """
        if self.sfx not in ("u8", "u16"):
            return
        totype = self.sfx[0]+str(int(self.sfx[1:])*2)
        expand = getattr(self.npyv, f"expand_{totype}_{self.sfx}")
        # close enough from the edge to detect any deviation
        data  = self._data(self._int_max() - self.nlanes)
        vdata = self.load(data)
        edata = expand(vdata)
        # lower half part
        data_lo = data[:self.nlanes//2]
        # higher half part
        data_hi = data[self.nlanes//2:]
        assert edata == (data_lo, data_hi)

    def test_arithmetic_subadd(self):
        if self._is_fp():
            data_a = self._data()
        else:
            data_a = self._data(self._int_max() - self.nlanes)
        data_b = self._data(self._int_min(), reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        # non-saturated
        data_add = self.load([a + b for a, b in zip(data_a, data_b)]) # load to cast
        add  = self.add(vdata_a, vdata_b)
        assert add == data_add
        data_sub  = self.load([a - b for a, b in zip(data_a, data_b)])
        sub  = self.sub(vdata_a, vdata_b)
        assert sub == data_sub

    def test_arithmetic_mul(self):
        if self.sfx in ("u64", "s64"):
            return

        if self._is_fp():
            data_a = self._data()
        else:
            data_a = self._data(self._int_max() - self.nlanes)
        data_b = self._data(self._int_min(), reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        data_mul = self.load([a * b for a, b in zip(data_a, data_b)])
        mul = self.mul(vdata_a, vdata_b)
        assert mul == data_mul

    def test_arithmetic_div(self):
        if not self._is_fp():
            return

        data_a, data_b = self._data(), self._data(reverse=True)
        vdata_a, vdata_b = self.load(data_a), self.load(data_b)

        # load to truncate f64 to precision of f32
        data_div = self.load([a / b for a, b in zip(data_a, data_b)])
        div = self.div(vdata_a, vdata_b)
        assert div == data_div

    def test_arithmetic_intdiv(self):
        """
        Test integer division intrinsics:
            npyv_divisor_##sfx
            npyv_divc_##sfx
        """
        if self._is_fp():
            return

        int_min = self._int_min()
        def trunc_div(a, d):
            """
            Divide towards zero works with large integers > 2^53,
            and wrap around overflow similar to what C does.
            """
            if d == -1 and a == int_min:
                return a
            sign_a, sign_d = a < 0, d < 0
            if a == 0 or sign_a == sign_d:
                return a // d
            return (a + sign_d - sign_a) // d + 1

        data = [1, -int_min]  # to test overflow
        data += range(0, 2**8, 2**5)
        data += range(0, 2**8, 2**5-1)
        bsize = self._scalar_size()
        if bsize > 8:
            data += range(2**8, 2**16, 2**13)
            data += range(2**8, 2**16, 2**13-1)
        if bsize > 16:
            data += range(2**16, 2**32, 2**29)
            data += range(2**16, 2**32, 2**29-1)
        if bsize > 32:
            data += range(2**32, 2**64, 2**61)
            data += range(2**32, 2**64, 2**61-1)
        # negate
        data += [-x for x in data]
        for dividend, divisor in itertools.product(data, data):
            divisor = self.setall(divisor)[0]  # cast
            if divisor == 0:
                continue
            dividend = self.load(self._data(dividend))
            data_divc = [trunc_div(a, divisor) for a in dividend]
            divisor_parms = self.divisor(divisor)
            divc = self.divc(dividend, divisor_parms)
            assert divc == data_divc

    def test_arithmetic_reduce_sum(self):
        """
        Test reduce sum intrinsics:
            npyv_sum_##sfx
        """
        if self.sfx not in ("u32", "u64", "f32", "f64"):
            return
        # reduce sum
        data = self._data()
        vdata = self.load(data)

        data_sum = sum(data)
        vsum = self.sum(vdata)
        assert vsum == data_sum

    def test_arithmetic_reduce_sumup(self):
        """
        Test extend reduce sum intrinsics:
            npyv_sumup_##sfx
        """
        if self.sfx not in ("u8", "u16"):
            return
        rdata = (0, self.nlanes, self._int_min(), self._int_max()-self.nlanes)
        for r in rdata:
            data = self._data(r)
            vdata = self.load(data)
            data_sum = sum(data)
            vsum = self.sumup(vdata)
            assert vsum == data_sum

    def test_mask_conditional(self):
        """
        Conditional addition and subtraction for all supported data types.
        Test intrinsics:
            npyv_ifadd_##SFX, npyv_ifsub_##SFX
        """
        vdata_a = self.load(self._data())
        vdata_b = self.load(self._data(reverse=True))
        true_mask  = self.cmpeq(self.zero(), self.zero())
        false_mask = self.cmpneq(self.zero(), self.zero())

        data_sub = self.sub(vdata_b, vdata_a)
        ifsub = self.ifsub(true_mask, vdata_b, vdata_a, vdata_b)
        assert ifsub == data_sub
        ifsub = self.ifsub(false_mask, vdata_a, vdata_b, vdata_b)
        assert ifsub == vdata_b

        data_add = self.add(vdata_b, vdata_a)
        ifadd = self.ifadd(true_mask, vdata_b, vdata_a, vdata_b)
        assert ifadd == data_add
        ifadd = self.ifadd(false_mask, vdata_a, vdata_b, vdata_b)
        assert ifadd == vdata_b

bool_sfx = ("b8", "b16", "b32", "b64")
int_sfx = ("u8", "s8", "u16", "s16", "u32", "s32", "u64", "s64")
fp_sfx  = ("f32", "f64")
all_sfx = int_sfx + fp_sfx
tests_registry = {
    bool_sfx: _SIMD_BOOL,
    int_sfx : _SIMD_INT,
    fp_sfx  : _SIMD_FP,
    ("f32",): _SIMD_FP32,
    ("f64",): _SIMD_FP64,
    all_sfx : _SIMD_ALL
}
for target_name, npyv in targets.items():
    simd_width = npyv.simd if npyv else ''
    pretty_name = target_name.split('__') # multi-target separator
    if len(pretty_name) > 1:
        # multi-target
        pretty_name = f"({' '.join(pretty_name)})"
    else:
        pretty_name = pretty_name[0]

    skip = ""
    skip_sfx = dict()
    if not npyv:
        skip = f"target '{pretty_name}' isn't supported by current machine"
    elif not npyv.simd:
        skip = f"target '{pretty_name}' isn't supported by NPYV"
    elif not npyv.simd_f64:
        skip_sfx["f64"] = f"target '{pretty_name}' doesn't support double-precision"

    for sfxes, cls in tests_registry.items():
        for sfx in sfxes:
            skip_m = skip_sfx.get(sfx, skip)
            inhr = (cls,)
            attr = dict(npyv=targets[target_name], sfx=sfx, target_name=target_name)
            tcls = type(f"Test{cls.__name__}_{simd_width}_{target_name}_{sfx}", inhr, attr)
            if skip_m:
                pytest.mark.skip(reason=skip_m)(tcls)
            globals()[tcls.__name__] = tcls
