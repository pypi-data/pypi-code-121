class shape:
    """
    Animation shape class.

    See Also
    --------
    frame
    animate
    """

    def __init__(self, x = 0.0, y = 0.0, stroke = 1.0, color = 0x000,
            alpha = 1.0, T_Sa = 1.0):
        """
        Initialize the shape object.

        Parameters
        ----------
        x : float or array_like, default 0.0
            x values of the shape or the x-axis radius of an ellipse.
        y : float or array_like, default 0.0
            y values of the shape or the y-axis radius of an ellipse.
        stroke : float or array_like, default 1.0
            Stroke width or animated widths.
        color : float or array_like, default 0x000
            Stroke or fill color or animated colors.  It is a fill color or
            colors if `stroke` is a scalar zero.
        alpha : float or array_like, default 1.0
            Opacity or animated opacity values.  0.0 means fully transparent and
            1.0 means fully opaque.
        T_Sa : float, default 1.0
            Sampling period in seconds.
        """

        def to_ints(x):
            """
            Convert x to an integer or array of integers.
            """

            if np.ndim(x) == 0:
                x = int(x)
            if isinstance(x, list):
                x = np.array(x, dtype=int)
            return x

        def to_floats(x):
            """
            Convert x to a float or array of floats.
            """

            if (np.ndim(x) == 0):
                x = float(x)
            if isinstance(x, list):
                x = np.array(x, dtype=float)
            return x

        # Ensure x, y, stroke, and alpha are either floats or ndarrays.  Ensure
        # color is either an int or an ndarray.
        x = to_floats(x)
        y = to_floats(y)
        stroke = to_floats(stroke)
        color = to_ints(color)
        alpha = to_floats(alpha)

        # Ensure if either x or y is an ndarray, they both are.
        if isinstance(x, float) and isinstance(y, np.ndarray):
            x = x*np.ones(len(y))
        elif isinstance(x, np.ndarray) and isinstance(y, float):
            y = y*np.ones(len(x))

        # Ensure x and y are the same length.
        if isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            if len(x) != len(y):
                raise Exception('shape: x and y must be the same length!')

        # Ensure stroke, color, and alpha are non-negative and that alpha is not
        # more than one.
        if isinstance(stroke, float):
            if stroke < 0.0:
                stroke = 0.0
        else:
            stroke[stroke < 0.0] = 0.0
        if isinstance(color, int):
            if color < 0:
                color = 0
            elif color > 0xffffff:
                color = 0xffffff
        else:
            color[color < 0] = 0
            color[color > 0xffffff] = 0xffffff
        if isinstance(alpha, float):
            if alpha < 0.0:
                alpha = 0.0
            elif alpha > 1.0:
                alpha = 1.0
        else:
            alpha[alpha < 0.0] = 0.0
            alpha[alpha > 1.0] = 1.0

        # If stroke, color, or alpha are arrays and T_Sa is None, default to 1.
        if (isinstance(stroke, np.ndarray) or isinstance(color, np.ndarray) or \
                isinstance(alpha, np.ndarray)) and (T_Sa is None):
            T_Sa = 1

        # Add these parameters to the object.
        self.x = x
        self.y = y
        self.stroke = stroke
        self.color = color
        self.alpha = alpha
        self.T_Sa = T_Sa


class frame:
    """
    Animation shape class.

    See Also
    --------
    shape
    animate
    """

    def __init__(self, objs, x = 0.0, y = 0.0, ang = 0.0, scale = 1.0,
            T_Sa = 1.0):
        """
        Initialize the frame object.

        Parameters
        ----------
        objs : shape or frame or list of such
            A single shape or frame object or a list of such objects.
        x : float or array_like, default 0.0
            x-axis values of translation of the objects within the frame.
        y : float or array_like, default 0.0
            y-axis values of translation of the objects within the frame.
        ang : float or array_like, default 0.0
            Angles of rotation of the objects within the frame in radians.
        scale : float or array_like, default 1.0
            Scaling factors of the objects within the frame.
        T_Sa : float, default 1.0
            Sampling period in seconds.
        """

        # Ensure objs is a list.
        if isinstance(objs, (shape, frame)):
            objs = [objs]

        def to_floats(x):
            """
            Convert x to a float or array of floats.
            """

            if np.ndim(x) == 0:
                x = float(x)
            if isinstance(x, list):
                x = np.array(x, dtype=float)
            return x

        # Ensure x, y, ang, and scale are either floats or ndarrays.
        x = to_floats(x)
        y = to_floats(y)
        ang = to_floats(ang)
        scale = to_floats(scale)

        # Ensure if either x or y is an ndarray, they both are.
        if isinstance(x, float) and isinstance(y, np.ndarray):
            x = x*np.ones(len(y))
        elif isinstance(x, np.ndarray) and isinstance(y, float):
            y = y*np.ones(len(x))
        elif isinstance(x, np.ndarray) and isinstance(y, np.ndarray):
            if len(x) != len(y):
                raise Exception('frame: x and y must be the same length!')

        # Ensure scale is non-negative.
        if isinstance(scale, float):
            if scale < 0.0:
                scale = 0.0
        else:
            scale[scale < 0.0] = 0.0

        # If x, y, ang, or scale are arrays and T_Sa is None, default to 1.
        if (isinstance(x, np.ndarray) or isinstance(y, np.ndarray) or
                isinstance(ang, np.ndarray)) and (T_Sa is None):
            T_Sa = 1

        # Add these parameters to the object.
        self.objs = objs
        self.x = x
        self.y = y
        self.ang = ang
        self.scale = scale
        self.T_Sa = T_Sa


def jet_frames(x = 0.0, y = 0.0, ang = 0.0, force = 1.0,
        C0 = 0xF67926, C1 = 0xFFFBCE,
        width = 1.0, ratio = 4.0, cnt = 40, T_Sa = 0.05):
    """
    Create a list of animation frames, each one of a moving, fading bubble
    (circle), designed to imitate a jet of gas or fire.

    Parameters
    ----------
    x : float or array_like, default 0.0
        x position over time of jet source.
    y : float or array_like, default 0.0
        y position over time of jet source.
    ang : float or array_like, default 0.0
        Angle relative to x axis over time of jet source.  This is the opposite
        of the direction the jet bubbles move.
    C0 : int, default 0xF67926
        24-bit RGB color of bottom layer of bubbles.  The default is a dark
        orange.
    C1 : int, default 0xFFFBCE
        24-bit RGB color of top layer of bubbles.  The default is a bright
        yellow.
    width : float, default 1.0
        Width of jet.
    ratio : float, default 2.0
        Ratio of length to width of jet.
    cnt : int, default 50
        Number of bubbles to draw.
    T_Sa : float, default 0.05
        Sampling period in seconds.

    Returns
    -------
    obj_list : list of frame objects
        List of frame objects, each with one bubble (circle) shape.

    Notes
    -----
    The jet is by default pointed to the right (the bubbles move to the left),
    with the center of the starting point of the largest bubbles centered at
    `(0, 0)`.

    The bubbles are each within their own frame which loops about every second.
    The `x`, `y`, and `ang` arrays are used to then position and rotate those
    frames but only between the end and beginning of a bubble's loop.  The total
    duration of the animation is fixed.  Ideally, the duration of the bubble's
    loop would be an integer fraction of the total animation duration and an
    integer multiple of the sampling period.  However, if the total duration is
    a prime number multiple of the sampling period, this ideal is not possible.
    Something must give.  For the bubble animation to align with the total
    animation, the duration of the bubble loop must be an integer fraction of
    the total duration.  Therefore, the duration of the bubble loop cannot be
    guaranteed to be an integer multiple of the sampling period.  This means
    that `x`, `y`, and `ang` must be linearly interpolated over time to get the
    correct values at the beginnings of each bubble loop iteration.
    """

    # Convert x, y, or ang lists to np.ndarrays.
    if isinstance(x, list):
        x = np.array(x)
    if isinstance(y, list):
        y = np.array(y)
    if isinstance(ang, list):
        ang = np.array(ang)

    # Ensure x, y, and ang arrays are 1D and get their lengths.
    if isinstance(x, np.ndarray):
        if x.ndim > 1:
            x = x.flatten()
        N_x = len(x)
    else:
        N_x = 1
    if isinstance(y, np.ndarray):
        if y.ndim > 1:
            y = y.flatten()
        N_y = len(y)
    else:
        N_y = 1
    if isinstance(ang, np.ndarray):
        if ang.ndim > 1:
            ang = ang.flatten()
        N_ang = len(ang)
    else:
        N_ang = 1
    if isinstance(force, np.ndarray):
        if force.ndim > 1:
            force = force.flatten()
        N_force = len(force)
    else:
        N_force = 1

    # Ensure x, y, and ang arrays are the same shape.
    xy_diff = (N_x > 1) and (N_y > 1) and (N_x != N_y)
    xa_diff = (N_x > 1) and (N_ang > 1) and (N_x != N_ang)
    ya_diff = (N_y > 1) and (N_ang > 1) and (N_y != N_ang)
    if xy_diff or xa_diff or ya_diff:
        raise Exception('jet_frames: if x, y, or ang are arrays, ' +
                'they must be the same shape.')

    # Get the total duration of the animation.
    N_tot = max(N_x, N_y, N_ang)
    if N_tot == 1:
        T_tot = 5.0 # default duration [s]
        N = round(T_tot/T_Sa)
        T_tot = N*T_Sa
    else:
        T_tot = N_tot*T_Sa
        t_tot = np.arange(N_tot)*T_Sa # array of time for x, y, and ang

    # For each bubble,
    obj_list = []
    for n_bubble in range(cnt):
        # Get the duration of the bubble animation loop as an integer fraction
        # of the total duration.
        T_rep = 0.1 + 0.3*np.random.rand()
        N_reps = round(T_tot/T_rep)
        if N_reps < 1:
            N_reps = 1
        T_rep = T_tot/N_reps

        # Get the animation sampling period as an integer fraction of the
        # bubble animation loop duration.  It does not have to be T_Sa.
        T_ani = 0.01
        N_ani = round(T_rep/T_ani)
        if N_ani < 10:
            N_ani = 10
        T_ani = T_rep/N_ani

        # Get scaling factor.
        r = float(n_bubble)/(cnt - 1) # progress through the animation [0, 1]
        scale = np.linspace(1, 1.5, N_ani)*(1.0 - 0.5*r) # [1, 1.5], [0.5, 0.75]

        # Get the bubble x and y path values.
        length = width*ratio
        x_begin = 0.5*width*(1.0 - scale[0])
        x_end = -length*2*(1 + np.random.rand())/3
        x_bubble = np.linspace(x_begin, x_end, N_ani)
        y_end = (0.5*width)*np.random.randn()
        y_end -= np.round(y_end/width)*width
        y_bubble = np.linspace(0, y_end, N_ani)

        # Get alpha.
        alpha = np.linspace(1, 0, N_ani)
        alpha[0] = 0

        # Get color by averaging.
        color = mix_colors(C0, C1, r)

        # Define bubble (circle).
        curve = shape(0.5*width, 0.5*width, stroke = 0, color = color,
                alpha = alpha, T_Sa = T_ani)

        # Define bubble frame.
        bubble = frame(curve, x_bubble, y_bubble, scale=scale, T_Sa=T_ani)

        # Move and rotate the bubble frame for dynamic x, y, and ang.
        if N_tot > 1:
            # Get full animation time array.
            t_ani = np.arange(N_ani*N_reps)*T_ani

            # Interpolate to get x, y, and ang values at starts of bubble loops.
            t_reps = np.arange(N_reps)*T_rep
            if (N_x > 1):
                x_reps = np.interp(t_reps, t_tot, x)
                x_ani = np.zeros(len(t_ani))
                for n_rep in range(N_reps):
                    na = n_rep*N_ani
                    x_ani[na:(na + N_ani)] = x_reps[n_rep]
            else:
                x_ani = x
            if (N_y > 1):
                y_reps = np.interp(t_reps, t_tot, y)
                y_ani = np.zeros(len(t_ani))
                for n_rep in range(N_reps):
                    na = n_rep*N_ani
                    y_ani[na:(na + N_ani)] = y_reps[n_rep]
            else:
                y_ani = y
            if (N_ang > 1):
                ang_reps = np.interp(t_reps, t_tot, ang)
                ang_ani = np.zeros(len(t_ani))
                for n_rep in range(N_reps):
                    na = n_rep*N_ani
                    ang_ani[na:(na + N_ani)] = ang_reps[n_rep]
            else:
                ang_ani = ang
            if (N_force > 1):
                force_reps = np.interp(t_reps, t_tot, force)
                force_ani = np.zeros(len(t_ani))
                for n_rep in range(N_reps):
                    na = n_rep*N_ani
                    force_ani[na:(na + N_ani)] = force_reps[n_rep]
            else:
                force_ani = force

            # Put the bubble into another frame.
            bubble = frame(bubble, x_ani, y_ani, ang = ang_ani,
                    scale = force, T_Sa = T_ani)

        # Append to the list of cnt.
        obj_list.append(bubble)

    # Move and rotate the bubble frames for static x, y, and ang.
    if N_tot == 1:
        obj_list = frame(obj_list, x, y, ang)

    return obj_list


def animate(obj, filename='ani.svg', x_lim=[-1, 1], y_lim=[-1, 1]):
    """
    Create an svg (scalable vector graphics) animation file from the data stored
    in `obj`.

    Parameters
    ----------
    obj : shape object, frame object, or list of such objects
        The data to create an animation
    filename : string, default 'ani.svg'
        The desired name of output file.  End it with '.svg' in order for
        your system to automatically know how to open it.
    x_lim : array_like, default [-1, 1]
        A list or array of the minimum and maximum x values to display in
        the animation.
    y_lim : array_like, default [-1, 1]
        A list or array of the minimum and maximum y values to display in
        the animation.
    """

    def to_str(x):
        """
        Convert `x` from a float to a string or from an array of floats to a
        list of strings.
        """

        if isinstance(x, (np.ndarray, list)):
            return ['%.5g' % (x[n]) for n in range(len(x))]
        else:
            return '%.5g' % (x)

    def svg_color(C):
        """
        Convert `C` from a color integer to an svg-style color string or from an
        array of integers to a list of strings.
        """

        if isinstance(C, (np.ndarray, list)):
            return ['#' + hex(C[n])[2:].zfill(3) if (C[n] <= 0xfff) else
                    '#' + hex(C[n])[2:].zfill(6) for n in range(len(C))]
        else:
            return ('#' + hex(C)[2:].zfill(3) if (C <= 0xfff) else
                    '#' + hex(C)[2:].zfill(6))

    def keypoints(y, tol=0.0):
        """
        Find the array of indices of `y` where `y` changes slope by more than
        `tol`.  This includes the end points: 0 and N - 1.
        """

        # Get the indices of the starts of keypoints.
        dy = np.diff(y)
        ddy = np.diff(dy)
        n_start = np.nonzero(np.abs(ddy) > tol + 1e-12)[0] + 1

        # Build the full index array.
        nn = np.zeros(len(n_start) + 2, dtype=int)
        nn[1:-1] = n_start
        nn[-1] = len(y) - 1

        return nn

    def add_values(a, b = None, level = 1, pre = '', post = '', sep = '',
            end = ''):
        """
        Write the elements of list `a` (and of list `b` if it is not `None`).

        Parameters
        ----------
        a : string array_like
            First list of strings of values to add.
        b : string array_like, default None
            Second list of strings of values to add.
        level : int, default 1
            Indentation level.
        pre : string, default ''
            String to place before any values.
        post : string, default ''
            String to place after the first or first pair of values.
        sep : string, default ''
            String (besides space) to place between values or pairs of values.
        end : string, default ''
            String  to place after the last value or pair of values.
        """

        ind = '  '*level
        if b is None:
            text = ind + '\"' + pre + a[0] + post + sep + ' '
            for n in range(1, len(a) - 1):
                text += a[n]
                if len(text + sep + a[n + 1]) >= 80:
                    text += sep + '\n'
                    fid.write(text)
                    text = ind
                else:
                    text += sep + ' '
            text += a[-1] + end + '\"'
            fid.write(text)
        else:
            text = ind + '\"' + pre + a[0] + ',' + b[0] + post + sep + ' '
            for n in range(1, len(a) - 1):
                text += a[n] + ',' + b[n]
                if len(text + sep + a[n + 1] + ',' + b[n + 1]) >= 80:
                    text += sep + '\n'
                    fid.write(text)
                    text = ind
                else:
                    text += sep + ' '
            text += a[-1] + ',' + b[-1] + end + '\"'
            fid.write(text)

    def dynamic_translate(obj, scale_post, level):
        """
        Add translation (x or y movement) animation.

        Parameters
        ----------
        obj : frame
            Frame object with `x` and `y` position arrays and `T_Sa` sampling
            period.
        scale_post : float
            Scaling factor that will be applied to the whole frame.
        level : int
            Indentation level.
        """

        # Introduce the animation.
        ind = '  '*level
        fid.write('%s<animateTransform\n' % (ind))
        fid.write('%s  attributeName=\"transform\"\n' % (ind))
        fid.write('%s  type=\"translate\"\n' % (ind))
        fid.write('%s  additive=\"sum\"\n' % (ind))
        fid.write('%s  repeatCount=\"indefinite\"\n' % (ind))
        fid.write('%s  dur=\"%.15gs\"\n' % (ind, len(obj.x)*obj.T_Sa))

        # Get the scaled animation values and key-point indices.
        px =  np.append(obj.x, obj.x[0])*p_scale/scale_post
        py = -np.append(obj.y, obj.y[0])*p_scale/scale_post
        nn_px_keys = keypoints(px)
        nn_py_keys = keypoints(py)
        nn_keys = np.unique(np.concatenate((nn_px_keys, nn_py_keys)))

        # Write the values at key points or write all the values.
        if len(nn_keys) < len(px)*0.5:
            fid.write('%s  keyTimes=\n' % (ind))
            key_times = nn_keys/float(len(px) - 1)
            key_times[-1] = 1
            key_times = to_str(key_times)
            add_values(key_times, None, level + 2, sep=';')
            fid.write('\n%s  values=\n' % (ind))
            px = to_str(px[nn_keys])
            py = to_str(py[nn_keys])
            add_values(px, py, level + 2, sep=';')
        else:
            fid.write('%s  values=\n' % (ind))
            px = to_str(px)
            py = to_str(py)
            add_values(px, py, level + 2, sep=';')
        fid.write('/>\n')

    def dynamic_rotate(obj, level):
        """
        Add rotation animation.

        Parameters
        ----------
        obj : frame
            Frame object with `ang` rotation array and `T_Sa` sampling period.
        level : int
            Indentation level.

        Notes
        -----
        Although this is meant for dynamic rotation only, if there is also
        dynamic translation, a static rotation cannot be performed in the group
        opening instructions because that will cause the rotation to occur after
        the translation.  We always want the rotation to occur before the
        translation.  So, only this dynamic also handles some static cases.
        """

        # Introduce the animation.
        ind = '  '*level
        fid.write('%s<animateTransform\n' % (ind))
        fid.write('%s  attributeName=\"transform\"\n' % (ind))
        fid.write('%s  type=\"rotate\"\n' % (ind))
        fid.write('%s  additive=\"sum\"\n' % (ind))
        fid.write('%s  repeatCount=\"indefinite\"\n' % (ind))
        fid.write('%s  dur=\"%.15gs\"\n' % (ind, len(obj.ang)*obj.T_Sa))

        # Get the scaled animation values and key-point indices.
        ang = -np.unwrap(np.append(obj.ang, obj.ang[0]))*RAD_TO_DEG
        nn_keys = keypoints(ang)

        # Write the values at key points or write all the values.
        if len(ang) == 2: # for static rotation before dynamic translation
            fid.write('%s  values=\"%.3g\"' % (ind, ang[0]))
        elif len(nn_keys) < len(ang)*0.5:
            fid.write('%s  keyTimes=\n' % (ind))
            key_times = nn_keys/float(len(ang) - 1)
            key_times[-1] = 1
            key_times = to_str(key_times)
            add_values(key_times, None, level + 2, sep=';')
            fid.write('\n%s  values=\n' % (ind))
            ang = to_str(ang[nn_keys])
            add_values(ang, None, level + 2, sep=';')
        else:
            fid.write('%s  values=\n' % (ind))
            ang = to_str(ang)
            add_values(ang, None, level + 2, sep=';')
        fid.write('/>\n')

    def dynamic_scale(obj, scale_post, level):
        """
        Add scaling factor animation.

        Parameters
        ----------
        obj : frame
            Frame object with `scale` factor array and `T_Sa` sampling period.
        scale_post : float
            Scaling factor that will be applied to the whole frame.
        level : int
            Indentation level.
        """

        # Introduce the animation.
        ind = '  '*level
        fid.write('%s<animateTransform\n' % (ind))
        fid.write('%s  attributeName=\"transform\"\n' % (ind))
        fid.write('%s  type=\"scale\"\n' % (ind))
        fid.write('%s  additive=\"sum\"\n' % (ind))
        fid.write('%s  repeatCount=\"indefinite\"\n' % (ind))
        fid.write('%s  dur=\"%.15gs\"\n' % (ind, len(obj.scale)*obj.T_Sa))

        # Get the scaled animation values and key-point indices.
        scales = np.append(obj.scale, obj.scale[0])/scale_post
        nn_keys = keypoints(scales)

        # Write the values at key points or write all the values.
        if len(nn_keys) < len(scales)*0.5:
            fid.write('%s  keyTimes=\n' % (ind))
            key_times = nn_keys/float(len(scales) - 1)
            key_times[-1] = 1
            key_times = to_str(key_times)
            add_values(key_times, None, level + 2, sep=';')
            fid.write('\n%s  values=\n' % (ind))
            scales = to_str(scales[nn_keys])
            add_values(scales, None, level + 2, sep=';')
        else:
            fid.write('%s  values=\n' % (ind))
            scales = to_str(scales)
            add_values(scales, None, level + 2, sep=';')
        fid.write('/>\n')

    def dynamic_stroke(obj, level):
        """
        Add stroke width animation.

        Parameters
        ----------
        obj : shape
            Shape object with `stroke` width array and `T_Sa` sampling period.
        level : int
            Indentation level.
        """

        # Introduce the animation.
        ind = '  '*level
        fid.write('%s<animate\n' % (ind))
        fid.write('%s  attributeName=\"stroke-width\"\n' % (ind))
        fid.write('%s  repeatCount=\"indefinite\"\n' % (ind))
        fid.write('%s  dur=\"%.15gs\"\n' % (ind, len(obj.stroke)*obj.T_Sa))

        # Get the scaled animation values and key-point indices.
        strokes = np.append(obj.stroke, obj.stroke[0])*p_scale
        nn_keys = keypoints(strokes)

        # Write the values at key points or write all the values.
        if len(nn_keys) < len(strokes)*0.5:
            fid.write('%s  keyTimes=\n' % (ind))
            key_times = nn_keys/float(len(strokes) - 1)
            key_times[-1] = 1
            key_times = to_str(key_times)
            add_values(key_times, None, level + 2, '', '', ';', '')
            fid.write('\n%s  values=\n' % (ind))
            strokes = to_str(strokes[nn_keys])
            add_values(strokes, None, level + 2, '', '', ';', '')
        else:
            fid.write('%s  values=\n' % (ind))
            strokes = to_str(strokes)
            add_values(strokes, None, level + 2, '', '', ';', '')
        fid.write('/>\n')

    def dynamic_color(obj, level):
        """
        Add stroke or fill color animation.  Which is determined by the `stroke`
        value.

        Parameters
        ----------
        obj : shape
            Shape object with `color` and `stroke` width arrays and `T_Sa`
            sampling period.
        level : int
            Indentation level.
        """

        # Introduce the animation.
        ind = '  '*level
        fid.write('%s<animate\n' % (ind))
        if isinstance(obj.stroke, float) and (obj.stroke <= 0):
            fid.write('%s  attributeName=\"fill\"\n' % (ind))
        else:
            fid.write('%s  attributeName=\"stroke\"\n' % (ind))
        fid.write('%s  repeatCount=\"indefinite\"\n' % (ind))
        fid.write('%s  dur=\"%.15gs\"\n' % (ind, len(obj.color)*obj.T_Sa))

        # Get the scaled animation values and key-point indices.
        colors = np.append(obj.color, obj.color[0])
        nn_keys = keypoints(colors)

        # Write the values at key points or write all the values.
        if len(nn_keys) < len(colors)*0.5:
            fid.write('%s  keyTimes=\n' % (ind))
            key_times = nn_keys/float(len(colors) - 1)
            key_times[-1] = 1
            key_times = to_str(key_times)
            add_values(key_times, None, level + 2, '', '', ';', '')
            fid.write('\n%s  values=\n' % (ind))
            colors = svg_color(colors)
            add_values(colors, None, level + 2, '', '', ';', '')
        else:
            fid.write('%s  values=\n' % (ind))
            colors = svg_color(colors)
            add_values(colors, None, level + 2, '', '', ';', '')
        fid.write('/>\n')

    def dynamic_alpha(obj, level):
        """
        Add alpha (opacity) animation.

        Parameters
        ----------
        obj : shape
            Shape object with `alpha` array and `T_Sa` sampling period.
        level : int
            Indentation level.
        """

        # Introduce the animation.
        ind = '  '*level
        fid.write('%s<animate\n' % (ind))
        fid.write('%s  attributeName=\"opacity\"\n' % (ind))
        fid.write('%s  repeatCount=\"indefinite\"\n' % (ind))
        fid.write('%s  dur=\"%.15gs\"\n' % (ind, len(obj.alpha)*obj.T_Sa))

        # Get the scaled animation values and key-point indices.
        alphas = np.append(obj.alpha, obj.alpha[0])
        nn_keys = keypoints(alphas)

        # Write the values at key points or write all the values.
        if len(nn_keys) < len(alphas)*0.5:
            fid.write('%s  keyTimes=\n' % (ind))
            key_times = nn_keys/float(len(alphas) - 1)
            key_times[-1] = 1
            key_times = to_str(key_times)
            add_values(key_times, None, level + 2, '', '', ';', '')
            fid.write('\n%s  values=\n' % (ind))
            alphas = to_str(alphas[nn_keys])
            add_values(alphas, None, level + 2, '', '', ';', '')
        else:
            fid.write('%s  values=\n' % (ind))
            alphas = to_str(alphas)
            add_values(alphas, None, level + 2, '', '', ';', '')
        fid.write('/>\n')

    def add_shape(obj, level):
        """
        Add shape object details: the shape itself as defined by (`x`,`y`),
        `stroke` width, stroke or fill `color`, and `alpha`.

        Parameters
        ----------
        obj : shape
            Shape object.
        level : int
            Indentation level.

        Notes
        -----
        First, the type of shape needs to be determined.  If (`x`,`y`) is a
        single pair of scalar values, then this is either a circle or and
        ellipse where `x` is the x-axis radius and `y` is the y-axis radius.  If
        `x` equals `y` then it is a circle, and if not, then it is an ellipse.
        If (`x`,`y`) is a pair of vectors, then a generic path is created.

        Second, any static properties of the shape are specified.

        Third, the shape itself is defined.

        Finally, any dynamic properties are specified.
        """

        # Start the shape.
        ind = '  '*level
        if isinstance(obj.x, float):
            if obj.x == obj.y:
                fid.write('%s<circle\n' % (ind))
            else:
                fid.write('%s<ellipse\n' % (ind))
        else:
            fid.write('%s<path\n' % (ind))

        # Write the static stroke, color, and alpha.
        if isinstance(obj.stroke, float) and (obj.stroke <= 0):
            do_fill = True
        else:
            do_fill = False
        if not do_fill:
            fid.write('%s  vector-effect=\"non-scaling-stroke\"\n' % (ind))
            fid.write('%s  fill-opacity=\"0\"\n' % (ind))
            fid.write('%s  stroke-linecap=\"round\"\n' % (ind))
            fid.write('%s  stroke-linejoin=\"round\"\n' % (ind))
        if isinstance(obj.stroke, float):
            fid.write('%s  stroke-width=\"%.3g\"\n' %
                    (ind, obj.stroke*p_scale))
        if isinstance(obj.color, int):
            color_str = svg_color(obj.color)
            if do_fill:
                fid.write('%s  fill=\"%s\"\n' % (ind, color_str))
            else:
                fid.write('%s  stroke=\"%s\"\n' % (ind, color_str))
        if isinstance(obj.alpha, float) and (obj.alpha != 1):
            fid.write('%s  opacity=\"%s\"\n' % (ind, to_str(obj.alpha)))

        # Write the x and y values.
        if isinstance(obj.x, float):
            if (obj.x == obj.y):
                fid.write('%s  r=\"%.3g\"' % (ind, abs(obj.x*p_scale)))
            else:
                fid.write('%s  rx=\"%.3g\"\n' % (ind, abs(obj.x*p_scale)))
                fid.write('%s  ry=\"%.3g\"' % (ind, abs(obj.y*p_scale)))
        else:
            fid.write('%s  d=\n' % (ind))
            px = to_str( obj.x*p_scale)
            py = to_str(-obj.y*p_scale)
            if do_fill:
                add_values(px, py, level + 2, 'M ', ' L', '', ' z')
            else:
                add_values(px, py, level + 2, 'M ', ' L', '', '')

        # Write the ending with any dynamics.
        if isinstance(obj.stroke, float) and isinstance(obj.color, int) and \
                isinstance(obj.alpha, float):
            fid.write('/>\n')
        else:
            fid.write('>\n')
            if isinstance(obj.stroke, np.ndarray):
                dynamic_stroke(obj, level + 1)
            if isinstance(obj.color, np.ndarray):
                dynamic_color(obj, level + 1)
            if isinstance(obj.alpha, np.ndarray):
                dynamic_alpha(obj, level + 1)
            if not isinstance(obj.x, np.ndarray):
                if obj.x == obj.y:
                    fid.write('%s</circle>\n' % (ind))
                else:
                    fid.write('%s</ellipse>\n' % (ind))
            else:
                fid.write('%s</path>\n' % (ind))

    def add_obj(obj, level):
        """
        Add the shape, frame, or list of such to the svg file.

        Parameters
        ----------
        obj : shape, frame, or list of such
            A shape or frame object or a list of such objects to be added to the
            svg file.
        level : int
            Indentation level.

        Notes
        -----
        If the object is a frame, create an svg group, specify any static
        translate, rotate, or scale properties, add the child objects, add any
        dynamic (animated) translate, rotate, or scale properties, and close the
        group.  To avoid visual distortions visible in some web browsers due to
        animated down-scaling, get the minimum animated scaling factor, divide
        all the animated scaling factor values by this minimum so that the new
        minimum is 1, and post scale down the whole group.  The `scale_post` is
        this minimum scaling factor.

        If the object is a shape, add the shape.

        If the object is a list, call this function on each of the members.
        """

        # Get the indent string.
        ind = '  '*level

        if isinstance(obj, frame):
            # Open the group.
            fid.write('%s<g' % (ind))

            # Get static flags.
            xy_static = isinstance(obj.x, (float, int))
            ang_static = isinstance(obj.ang, (float, int))
            scale_static = isinstance(obj.scale, (float, int))

            # Get the post scaling factor.
            if not scale_static:
                scale_post = np.min(obj.scale)
                if scale_post < 1e-3:
                    scale_post = 1e-3
                if abs(scale_post - 1) < 1e-3:
                    scale_post = 1.0
            else:
                scale_post = 1.0

            # Write any static settings.  This includes static down-scaling
            # after dynamic up-scaling (to overcome artifacts in Safari).
            if (xy_static and ((obj.x != 0) or (obj.y != 0))) or \
                    (xy_static and ang_static) or \
                    (scale_static and (obj.scale != 1)) or (scale_post != 1):
                fid.write(' transform=\"')
                is_first = True
                if xy_static and ((obj.x != 0) or (obj.y != 0)):
                    fid.write('translate(%.3f,%.3f)' %
                            (obj.x*p_scale, -obj.y*p_scale))
                    is_first = False
                if xy_static and ang_static and (obj.ang != 0):
                    ang = -obj.ang*RAD_TO_DEG
                    if not is_first:
                        fid.write(' ')
                    fid.write('rotate(%.3f)' % (ang))
                    is_first = False
                if scale_static and (obj.scale != 1):
                    if not is_first:
                        fid.write(' ')
                    fid.write('scale(%.3f)' % (obj.scale*p_scale))
                elif scale_post != 1:
                    if not is_first:
                        fid.write(' ')
                    fid.write('scale(%.3f)' % (scale_post))
                fid.write('\"')
            fid.write('>\n')

            # Add the objects in this group.
            for child in obj.objs:
                add_obj(child, level + 1)

            # Add dynamic settings.
            if not xy_static:
                dynamic_translate(obj, scale_post, level + 1)
                if ang_static and (obj.ang != 0):
                    obj.ang = [obj.ang]
                    dynamic_rotate(obj, level + 1)
            if not ang_static:
                dynamic_rotate(obj, level + 1)
            if not scale_static:
                dynamic_scale(obj, scale_post, level + 1)

            # Close the group.
            fid.write('%s</g>\n' % (ind))
        elif isinstance(obj, shape):
            add_shape(obj, level)
        elif isinstance(obj, list):
            for child in obj:
                add_obj(child, level + 1)

    # Ensure 'obj' is a list.
    if isinstance(obj, (shape, frame)):
        obj = [obj]

    # Get the window width and height.
    x_span = x_lim[1] - x_lim[0]
    y_span = y_lim[1] - y_lim[0]
    win_width = 640
    win_height = round(win_width*y_span/x_span)

    # Get the overall pixel scaling factor.
    p_scale = win_width/x_span

    # Get the input x and y shifts to the middle point.
    x_shift = (x_lim[1] + x_lim[0])/2.0
    y_shift = (y_lim[1] + y_lim[0])/2.0

    # Write the file.
    with open(filename, 'w') as fid:
        fid.write('<svg viewBox=\"%d %d %d %d\"\n' %
                (-win_width/2.0, -win_height/2.0, win_width, win_height))
        fid.write('  xmlns=\"http://www.w3.org/2000/svg\">\n')
        level = 1
        if (x_shift != 0) or (y_shift != 0):
            fid.write('  <g transform=\"translate(%.3g,%.3g)\">\n' %
                    (-x_shift*p_scale, y_shift*p_scale))
            level += 1

        # Crawl through the hierarchy of frames and objects and add them to the
        # animation.
        for child in obj:
            add_obj(child, level)

        # closing
        if level > 1:
            fid.write('  </g>\n')
        fid.write('</svg>\n')
        fid.close()
