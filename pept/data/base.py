#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#    pept is a Python library that unifies Positron Emission Particle
#    Tracking (PEPT) research, including tracking, simulation, data analysis
#    and visualisation tools
#
#    Copyright (C) 2019 Andrei Leonard Nicusan
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


# File   : base.py
# License: License: GNU v3.0
# Author : Andrei Leonard Nicusan <a.l.nicusan@bham.ac.uk>
# Date   : 19.08.2019


import  time
import  numpy                   as  np

import  plotly.graph_objects    as  go

import  matplotlib.pyplot       as  plt
from    matplotlib.colors       import Normalize
from    mpl_toolkits.mplot3d    import Axes3D


class LineData:
    '''A class for PEPT LoR data iteration, manipulation and visualisation.

    Generally, PEPT LoRs are lines in 3D space, each defined by two points,
    irrespective of the geometry of the scanner used. This class is used
    for LoRs (or any lines!) encapsulation. It can yield samples of the
    `line_data` of an adaptive `sample_size` and `overlap`, without requiring
    additional storage.

    Parameters
    ----------
    line_data : (N, 7) numpy.ndarray
        An (N, 7) numpy array that stores the PEPT LoRs (or any generic set of
        lines) as time and cartesian (3D) coordinates of two points defining each
        line, **in mm**. A row is then [time, x1, y1, z1, x2, y2, z2].
    sample_size : int, optional
        An `int`` that defines the number of lines that should be
        returned when iterating over `line_data`. A `sample_size` of 0
        yields all the data as one single sample. (Default is 200)
    overlap : int, optional
        An `int` that defines the overlap between two consecutive
        samples that are returned when iterating over `line_data`.
        An overlap of 0 means consecutive samples, while an overlap
        of (`sample_size` - 1) means incrementing the samples by one.
        A negative overlap means skipping values between samples. An
        error is raised if `overlap` is larger than or equal to
        `sample_size`. (Default is 0)
    verbose : bool, optional
        An option that enables printing the time taken for the
        initialisation of an instance of the class. Useful when
        reading large files (10gb files for PEPT data is not unheard
        of). (Default is True)

    Attributes
    ----------
    line_data : (N, 7) numpy.ndarray
        An (N, 7) numpy array that stores the PEPT LoRs as time and
        cartesian (3D) coordinates of two points defining a line, **in mm**.
        Each row is then `[time, x1, y1, z1, x2, y2, z2]`.
    sample_size : int
        An `int` that defines the number of lines that should be
        returned when iterating over `line_data`. (Default is 200)
    overlap : int
        An `int` that defines the overlap between two consecutive
        samples that are returned when iterating over `line_data`.
        An overlap of 0 means consecutive samples, while an overlap
        of (`sample_size` - 1) means incrementing the samples by one.
        A negative overlap means skipping values between samples. It
        is required to be smaller than `sample_size`. (Default is 0)
    number_of_lines : int
        An `int` that corresponds to len(`line_data`), or the number of
        LoRs stored by `line_data`.
    number_of_samples : int
        An `int` that corresponds to the number of samples that can be
        accessed from the class. It takes `overlap` into consideration.

    Raises
    ------
    ValueError
        If `overlap` >= `sample_size` unless `sample_size` is 0. Overlap
        has to be smaller than `sample_size`. Note that it can also be negative.
    ValueError
        If `line_data` does not have (N, 7) shape.

    Notes
    -----
    The class saves `line_data` as a **contiguous** numpy array for
    efficient access in C functions. It should not be changed after
    instantiating the class.

    '''

    def __init__(self,
                 line_data,
                 sample_size = 200,
                 overlap = 0,
                 verbose = False):

        if verbose:
            start = time.time()

        # If sample_size != 0 (in which case the class returns all data in one
        # sample), check the `overlap` is not larger or equal to `sample_size`.
        if sample_size != 0 and overlap >= sample_size:
            raise ValueError('\n[ERROR]: overlap = {} must be smaller than sample_size = {}\n'.format(overlap, sample_size))

        # Initialise the inner parameters of the class
        self._index = 0
        self._sample_size = sample_size
        self._overlap = overlap

        # If `line_data` is not C-contiguous, create a C-contiguous copy
        self._line_data = np.asarray(line_data, order = 'C', dtype = float)

        # Check that line_data has shape (N, 7)
        if self._line_data.ndim != 2 or self._line_data.shape[1] != 7:
            raise ValueError('\n[ERROR]: line_data should have dimensions (N, 7). Received {}\n'.format(self._line_data.shape))

        self._number_of_lines = len(self._line_data)

        if verbose:
            end = time.time()
            print("Initialising the PEPT data took {} seconds\n".format(end - start))


    @property
    def line_data(self):
        '''Get the lines stored in the class.

        Returns
        -------
        (, 7) numpy.ndarray
            A memory view of the lines stored in `line_data`.

        '''

        return self._line_data


    @property
    def sample_size(self):
        '''Get the number of lines in one sample returned by the class.

        Returns
        -------
        int
            The sample size (number of lines) in one sample returned by
            the class.

        '''

        return self._sample_size


    @sample_size.setter
    def sample_size(self, new_sample_size):
        '''Change `sample_size` without instantiating a new object

        It also resets the inner index of the class.

        Parameters
        ----------
        new_sample_size : int
            The new sample size. It has to be larger than `overlap`,
            unless it is 0 (in which case all `line_data` will be returned
            as one sample).

        Raises
        ------
        ValueError
            If `overlap` >= `new_sample_size`. Overlap has to be
            smaller than `sample_size`, unless `sample_size` is 0.
            Note that it can also be negative.

        '''

        if new_sample_size != 0 and self._overlap >= new_sample_size:
            raise ValueError('\n[ERROR]: overlap = {} must be smaller than new_sample_size = {}\n'.format(self._overlap, new_sample_size))

        self._index = 0
        self._sample_size = new_sample_size


    @property
    def overlap(self):
        '''Get the overlap between every two samples returned by the class.

        Returns
        -------
        int
            The overlap (number of lines) between every two samples  returned by
            the class.

        '''

        return self._overlap


    @overlap.setter
    def overlap(self, new_overlap):
        '''Change `overlap` without instantiating a new object

        It also resets the inner index of the class.

        Parameters
        ----------
        new_overlap : int
            The new overlap. It has to be smaller than `sample_size`, unless
            `sample_size` is 0 (in which case all `line_data` will be returned
            as one sample and so overlap does not play any role).

        Raises
        ------
        ValueError
            If `new_overlap` >= `sample_size`. `new_overlap` has to be
            smaller than `sample_size`, unless `sample_size` is 0.
            Note that it can also be negative.

        '''

        if self._sample_size != 0 and new_overlap >= self._sample_size:
            raise ValueError('\n[ERROR]: new_overlap = {} must be smaller than sample_size = {}\n'.format(new_overlap, self._sample_size))

        self._index = 0
        self._overlap = new_overlap


    @property
    def number_of_samples(self):
        '''Get number of samples, considering overlap.

        If `sample_size == 0`, all data is returned as a single sample,
        and so `number_of_samples` will be 1. Otherwise, it checks the
        number of samples every time it is called, taking `overlap` into
        consideration.

        Returns
        -------
        int
            The number of samples, taking `overlap` into consideration.

        '''
        # If self.sample_size == 0, all data is returned as a single sample
        if self._sample_size == 0:
            return 1

        # If self.sample_size != 0, check there is at least one sample
        if self._number_of_lines >= self._sample_size:
            return (self._number_of_lines - self._sample_size) // (self.sample_size - self.overlap) + 1
        else:
            return 0


    @property
    def number_of_lines(self):
        '''Get the number of lines stored in the class.

        Returns
        -------
        int
            The number of lines stored in `line_data`.

        '''
        return self._number_of_lines


    def sample_n(self, n):
        '''Get sample number n (indexed from 1, i.e. `n > 0`)

        Returns the lines from `line_data` included in sample number
        `n`. Samples are numbered starting from 1.

        Parameters
        ----------
        n : int
            The number of the sample required. Note that `1 <= n <=
            number_of_samples`.

        Returns
        -------
        (, 7) numpy.ndarray
            A shallow copy of the lines from `line_data` included in
            sample number n.

        Raises
        ------
        IndexError
            If `sample_size == 0`, all data is returned as one single
            sample. Raised if `n` is not 1.
        IndexError
            If `n > number_of_samples` or `n <= 0`.

        '''
        if self._sample_size == 0:
            if n == 1:
                return self._line_data
            else:
                raise IndexError("\n\n[ERROR]: Trying to access a non-existent sample (samples are indexed from 1): asked for sample number {}, when there is only 1 sample (sample_size == 0)\n".format(n))
        elif (n > self.number_of_samples) or n <= 0:
            raise IndexError("\n\n[ERROR]: Trying to access a non-existent sample (samples are indexed from 1): asked for sample number {}, when there are {} samples\n".format(n, self.number_of_samples))

        start_index = (n - 1) * (self._sample_size - self._overlap)
        return self._line_data[start_index:(start_index + self._sample_size)]


    def to_csv(self, filepath, delimiter = '  ', newline = '\n'):
        '''Write `line_data` to a CSV file

        Write all LoRs stored in the class to a CSV file.

        Parameters
        ----------
            filepath : filename or file handle
                If filepath is a path (rather than file handle), it is relative
                to where python is called.
            delimiter : str, optional
                The delimiter between values. The default is two spaces '  ',
                such that numbers in the format '123,456.78' are well-understood.
            newline : str, optional
                The sequence of characters at the end of every line. The default
                is a new line '\n'

        '''
        np.savetxt(filepath, self._line_data, delimiter = delimiter, newline = newline)


    def plot_all_lines(self, ax = None, color='r', alpha=1.0 ):
        '''Plot all lines using matplotlib

        Given a **mpl_toolkits.mplot3d.Axes3D** axis `ax`, plots all lines on it.

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.

        color : matplotlib color option (default 'r')

        alpha : matplotlib opacity option (default 1.0)

        Returns
        -------

        fig, ax : matplotlib figure and axes objects

        Note
        ----
        Plotting all lines in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `plot_lines_sample_n` is recommended.

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        p1 = self._line_data[:, 1:4]
        p2 = self._line_data[:, 4:7]

        for i in range(0, self._number_of_lines):
            ax.plot([ p1[i][0], p2[i][0] ],
                    [ p1[i][1], p2[i][1] ],
                    [ p1[i][2], p2[i][2] ],
                    c = color, alpha = alpha)

        return fig, ax


    def plot_all_lines_alt_axes(self, ax, color='r', alpha=1.0):
        '''Plot all lines using matplotlib on PEPT-style axes

        Given a **mpl_toolkits.mplot3d.Axes3D** axis `ax`, plots all lines on
        the PEPT-style convention: **x** is *parallel and horizontal* to the
        screens, **y** is *parallel and vertical* to the screens, **z** is
        *perpendicular* to the screens. The mapping relative to the
        Cartesian coordinates would then be: (x, y, z) -> (z, x, y)

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.

        color : matplotlib color option (default 'r')

        alpha : matplotlib opacity option (default 1.0)

        Returns
        -------

        fig, ax : matplotlib figure and axes objects

        Note
        ----
        Plotting all lines in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `plot_lines_sample_n_alt_axes` is recommended.

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()


        p1 = self._line_data[:, 1:4]
        p2 = self._line_data[:, 4:7]

        for i in range(0, self._number_of_lines):
            ax.plot([ p1[i][2], p2[i][2] ],
                    [ p1[i][0], p2[i][0] ],
                    [ p1[i][1], p2[i][1] ],
                    c = color, alpha=alpha)

        return fig, ax


    def plot_lines_sample_n(self, n, ax = None, color = 'r', alpha = 1.0):
        '''Plot lines from sample `n` using matplotlib

        Given a **mpl_toolkits.mplot3d.Axes3D** axis `ax`, plots all lines
        from sample number `n`.

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.

        sampleN : int
            The number of the sample to be plotted.

        color : matplotlib color option (default 'r')

        alpha : matplotlib opacity option (default 1.0)

        Returns
        -------

        fig, ax : matplotlib figure and axes objects

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        sample = self.sample_n(n)
        for i in range(0, len(sample)):
            ax.plot([ sample[i][1], sample[i][4] ],
                    [ sample[i][2], sample[i][5] ],
                    [ sample[i][3], sample[i][6] ],
                    c = color, alpha = alpha)

        return fig, ax


    def plot_lines_sample_n_alt_axes(self, n, ax=None, color='r', alpha=1.0):
        '''Plot lines from sample `n` using matplotlib on PEPT-style axes

        Given a **mpl_toolkits.mplot3d.Axes3D** axis `ax`, plots all lines from
        sample number sampleN on the PEPT-style coordinates convention:
        **x** is *parallel and horizontal* to the screens, **y** is
        *parallel and vertical* to the screens, **z** is *perpendicular*
        to the screens. The mapping relative to the Cartesian coordinates
        would then be: (x, y, z) -> (z, x, y)

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.
        n : int
            The number of the sample to be plotted.

        color : matplotlib color option (default 'r')

        alpha : matplotlib opacity option (default 1.0)

        Returns
        -------

        fig, ax : matplotlib figure and axes objects

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        sample = self.sample_n(n)
        for i in range(0, len(sample)):
            ax.plot([ sample[i][3], sample[i][6] ],
                    [ sample[i][1], sample[i][4] ],
                    [ sample[i][2], sample[i][5] ],
                    c = color, alpha = alpha)

        return fig, ax


    def all_lines_traces(self):
        '''Get a list of Plotly traces for each line.

        Creates a `plotly.graph_objects.Scatter3d` object for each line
        and returns them as a list. Can then be passed to the
        `plotly.graph_objects.figure.add_traces` function or a
        `PlotlyGrapher` instance using the `add_traces` method.

        Returns
        -------
        list
            A list of `plotly.graph_objects.Scatter3d` objects.

        Note
        ----
        Plotting all lines in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `lines_sample_n_traces` is recommended.

        '''

        p1 = self._line_data[:, 1:4]
        p2 = self._line_data[:, 4:7]

        traces = []
        for i in range(0, self._number_of_lines):
            traces.append(go.Scatter3d(
                x = [ p1[i][0], p2[i][0] ],
                y = [ p1[i][1], p2[i][1] ],
                z = [ p1[i][2], p2[i][2] ],
                mode = 'lines',
                opacity = 0.8,
                line = dict(
                    width = 2,
                )
            ))

        return traces


    def lines_sample_n_traces(self, n):
        '''Get a list of Plotly traces for each line in sample `n`.

        Creates a `plotly.graph_objects.Scatter3d` object for each line
        include in sample number `sampleN` and returns them as a list.
        Can then be passed to the `plotly.graph_objects.figure.add_traces`
        function or a `PlotlyGrapher` instance using the `add_traces` method.

        Parameters
        ----------
        n : int
            The number of the sample to be plotted.

        Returns
        -------
        list
            A list of `plotly.graph_objects.Scatter3d` objects.

        '''

        sample = self.sample_n(n)
        traces = []
        for i in range(0, len(sample)):
            traces.append(go.Scatter3d(
                x = [ sample[i][1], sample[i][4] ],
                y = [ sample[i][2], sample[i][5] ],
                z = [ sample[i][3], sample[i][6] ],
                mode = 'lines',
                opacity = 0.6,
                line = dict(
                    width = 2,
                )
            ))

        return traces


    def __len__(self):
        # Defined so that len(class_instance) returns the number of samples.

        return self.number_of_samples


    def __str__(self):
        # Shown when calling print(class)
        docstr = ""

        docstr += "sample_size = {}\n".format(self._sample_size)
        docstr += "overlap =     {}\n\n".format(self._overlap)
        docstr += "line_data = \n"
        docstr += self._line_data.__str__()

        return docstr


    def __repr__(self):
        # Shown when writing the class on a REPR

        docstr = "Class instance that inherits from `pept.LineData`.\n\n" + self.__str__() + "\n\n"
        docstr += "Particular cases:\n"
        docstr += " > If sample_size == 0, all line_data is returned as one single sample.\n"
        docstr += " > If overlap >= sample_size, an error is raised.\n"
        docstr += " > If overlap < 0, lines are skipped between samples.\n"

        return docstr


    def __getitem__(self, key):
        # Defined so that samples can be accessed as class_instance[0]

        if self.number_of_samples == 0:
            raise IndexError("Tried to access sample {} (indexed from 0), when there are {} samples".format(key, self.number_of_samples))

        if key >= self.number_of_samples:
            raise IndexError("Tried to access sample {} (indexed from 0), when there are {} samples".format(key, self.number_of_samples))


        while key < 0:
            key += self.number_of_samples

        return self.sample_n(key + 1)


    def __iter__(self):
        # Defined so the class can be iterated as `for sample in class_instance: ...`
        return self


    def __next__(self):
        # sample_size = 0 => return all data
        if self._sample_size == 0:
            self._sample_size = -1
            return self._line_data
        # Use -1 as a flag
        if self._sample_size == -1:
            self._sample_size = 0
            raise StopIteration

        # sample_size > 0 => return slices
        if self._index != 0:
            self._index = self._index + self._sample_size - self.overlap
        else:
            self._index = self._index + self.sample_size


        if self._index > self.number_of_lines:
            self._index = 0
            raise StopIteration

        return self._line_data[(self._index - self._sample_size):self._index]




class PointData:
    '''A class for generic PEPT data iteration, manipulation and visualisation.

    This class is used to encapsulate points. Unlike `LineData`, it does not have
    any restriction on the maximum number of columns it can store. It can yield
    samples of the `point_data` of an adaptive `sample_size` and `overlap`,
    without requiring additional storage.

    Parameters
    ----------
    point_data : (N, M) numpy.ndarray
        An (N, M >= 4) numpy array that stores points (or any generic 2D set of
        data). It expects that the first column is time, followed by cartesian
        (3D) coordinates of points **in mm**, followed by any extra information
        the user needs. A row is then [time, x, y, z, etc].
    sample_size : int, optional
        An `int`` that defines the number of points that should be
        returned when iterating over `point_data`. A `sample_size` of 0
        yields all the data as one single sample. (Default is 200)
    overlap : int, optional
        An `int` that defines the overlap between two consecutive
        samples that are returned when iterating over `point_data`.
        An overlap of 0 means consecutive samples, while an overlap
        of (`sample_size` - 1) means incrementing the samples by one.
        A negative overlap means skipping values between samples. An
        error is raised if `overlap` is larger than or equal to
        `sample_size`. (Default is 0)
    verbose : bool, optional
        An option that enables printing the time taken for the
        initialisation of an instance of the class. Useful when
        reading large files (10gb files for PEPT data is not unheard
        of). (Default is True)

    Attributes
    ----------
    point_data : (N, M) numpy.ndarray
        An (N, M >= 4) numpy array that stores the points as time, followed by
        cartesian (3D) coordinates of the point **in mm**, followed by any extra
        information. Each row is then `[time, x, y, z, etc]`.
    sample_size : int
        An `int` that defines the number of lines that should be
        returned when iterating over `point_data`. (Default is 200)
    overlap : int
        An `int` that defines the overlap between two consecutive
        samples that are returned when iterating over `point_data`.
        An overlap of 0 means consecutive samples, while an overlap
        of (`sample_size` - 1) means incrementing the samples by one.
        A negative overlap means skipping values between samples. It
        is required to be smaller than `sample_size`. (Default is 0)
    number_of_points : int
        An `int` that corresponds to len(`point_data`), or the number of
        points stored by `point_data`.
    number_of_samples : int
        An `int` that corresponds to the number of samples that can be
        accessed from the class, taking the `overlap` into consideration.

    Raises
    ------
    ValueError
        If `overlap` >= `sample_size`. Overlap is required to be smaller
        than `sample_size`, unless `sample_size` is 0. Note that it can
        also be negative.
    ValueError
        If `line_data` does not have (N, M) shape, where M >= 4.

    Notes
    -----
    The class saves `point_data` as a **contiguous** numpy array for
    efficient access in C extensions.

    '''


    def __init__(self,
                 point_data,
                 sample_size = 0,
                 overlap = 0,
                 verbose = False):

        if verbose:
            start = time.time()

        if sample_size != 0 and overlap >= sample_size:
            raise ValueError('\n[ERROR]: overlap = {} must be smaller than sample_size = {}\n'.format(overlap, sample_size))

        self._index = 0
        self._sample_size = sample_size
        self._overlap = overlap

        self._point_data = np.asarray(point_data, order = 'C', dtype = float)

        if self._point_data.ndim != 2 or self._point_data.shape[1] < 4:
            raise ValueError('\n[ERROR]: point_data should have two dimensions (M, N), where N >= 4. Received {}\n'.format(self._point_data.shape))

        self._number_of_points = len(self._point_data)

        if verbose:
            end = time.time()
            print("Initialising the PEPT data took {} seconds\n".format(end - start))


    @property
    def point_data(self):
        '''Get the points stored in the class.

        Returns
        -------
        (M, N) numpy.ndarray
            A memory view of the points stored in `point_data`.

        '''

        return self._point_data


    @property
    def sample_size(self):
        '''Get the number of points in one sample returned by the class.

        Returns
        -------
        int
            The sample size (number of lines) in one sample returned by
            the class.

        '''

        return self._sample_size


    @sample_size.setter
    def sample_size(self, new_sample_size):
        '''Change `sample_size` without instantiating a new object

        It also resets the inner index of the class.

        Parameters
        ----------
        new_sample_size : int
            The new sample size. It has to be larger than `overlap`,
            unless it is 0 (in which case all `point_data` will be returned
            as one sample).

        Raises
        ------
        ValueError
            If `overlap` >= `new_sample_size`. Overlap has to be
            smaller than `sample_size`, unless `sample_size` is 0.
            Note that it can also be negative.

        '''

        if new_sample_size != 0 and self._overlap >= new_sample_size:
            raise ValueError('\n[ERROR]: overlap = {} must be smaller than new_sample_size = {}\n'.format(self._overlap, new_sample_size))

        self._index = 0
        self._sample_size = new_sample_size


    @property
    def overlap(self):
        '''Get the overlap between every two samples returned by the class.

        Returns
        -------
        int
            The overlap (number of points) between every two samples  returned by
            the class.

        '''

        return self._overlap


    @overlap.setter
    def overlap(self, new_overlap):
        '''Change `overlap` without instantiating a new object

        It also resets the inner index of the class.

        Parameters
        ----------
        new_overlap : int
            The new overlap. It has to be smaller than `sample_size`, unless
            `sample_size` is 0 (in which case all `point_data` will be returned
            as one sample and so overlap does not play any role).

        Raises
        ------
        ValueError
            If `new_overlap` >= `sample_size`. `new_overlap` has to be
            smaller than `sample_size`, unless `sample_size` is 0.
            Note that it can also be negative.

        '''

        if self._sample_size != 0 and new_overlap >= self._sample_size:
            raise ValueError('\n[ERROR]: new_overlap = {} must be smaller than sample_size = {}\n'.format(new_overlap, self._sample_size))

        self._index = 0
        self._overlap = new_overlap


    @property
    def number_of_samples(self):
        '''Get number of samples, considering overlap.

        If `sample_size == 0`, all data is returned as a single sample,
        and so `number_of_samples` will be 1. Otherwise, it checks the
        number of samples every time it is called, taking `overlap` into
        consideration.

        Returns
        -------
        int
            The number of samples, taking `overlap` into consideration.

        '''
        # If self.sample_size == 0, all data is returned as a single sample
        if self._sample_size == 0:
            return 1

        # If self.sample_size != 0, check there is at least one sample
        if self._number_of_points >= self._sample_size:
            return (self._number_of_points - self._sample_size) // (self.sample_size - self.overlap) + 1
        else:
            return 0


    @property
    def number_of_points(self):
        '''Get the number of points stored in the class.

        Returns
        -------
        int
            The number of points stored in `point_data`.

        '''
        return self._number_of_points


    def sample_n(self, n):
        '''Get sample number n (indexed from 1, i.e. `n > 0`)

        Returns the lines from `point_data` included in sample number
        `n`. Samples are numbered starting from 1.

        Parameters
        ----------
        n : int
            The number of the sample required. Note that `1 <= n <=
            number_of_samples`.

        Returns
        -------
        (M, N) numpy.ndarray
            A shallow copy of the points from `point_data` included in
            sample number n.

        Raises
        ------
        IndexError
            If `sample_size == 0`, all data is returned as one single
            sample. Raised if `n` is not 1.
        IndexError
            If `n > number_of_samples` or `n <= 0`.

        '''
        if self._sample_size == 0:
            if n == 1:
                return self._point_data
            else:
                raise IndexError("\n\n[ERROR]: Trying to access a non-existent sample (samples indexed from 1): asked for sample number {}, when there is only 1 sample (sample_size == 0)\n".format(n))
        elif (n > self.number_of_samples) or n <= 0:
            raise IndexError("\n\n[ERROR]: Trying to access a non-existent sample (samples are indexed from 1): asked for sample number {}, when there are {} samples\n".format(n, self.number_of_samples))

        start_index = (n - 1) * (self._sample_size - self._overlap)
        return self._point_data[start_index:(start_index + self._sample_size)]


    def to_csv(self, filepath, delimiter = '  ', newline = '\n'):
        '''Write `point_data` to a CSV file

        Write all points (and any extra data) stored in the class to a CSV file.

        Parameters
        ----------
            filepath : filename or file handle
                If filepath is a path (rather than file handle), it is relative
                to where python is called.
            delimiter : str, optional
                The delimiter between values. The default is two spaces '  ',
                such that numbers in the format '123,456.78' are well-understood.
            newline : str, optional
                The sequence of characters at the end of every line. The default
                is a new line '\n'

        '''
        np.savetxt(filepath, self._point_data, delimiter = delimiter, newline = newline)


    def plot_all_points(self, ax = None):
        '''Plot all points using matplotlib

        Given a **mpl_toolkits.mplot3d.Axes3D** axis, plots all points on it.

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.

        Returns
        -------
        fig, ax : matplotlib figure and axes objects

        Note
        ----
        Plotting all points in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `plot_points_sample_n` is recommended.

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        # Scatter x, y, z, [color]

        x = self._point_data[:, 1],
        y = self._point_data[:, 2],
        z = self._point_data[:, 3],

        color = self._point_data[:, -1],

        cmap = plt.cm.magma
        color_array = cmap(colour_data)

        ax.scatter(x,y,z,c=color_array[0])

        return fig, ax


    def plot_all_points_alt_axes(self, ax = None ):
        '''Plot all points using matplotlib on PEPT-style axes

        Given a **mpl_toolkits.mplot3d.Axes3D** axis, plots all points on
        the PEPT-style convention: **x** is *parallel and horizontal* to the
        screens, **y** is *parallel and vertical* to the screens, **z** is
        *perpendicular* to the screens. The mapping relative to the
        Cartesian coordinates would then be: (x, y, z) -> (z, x, y)

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.

        Returns
        -------
        fig, ax : matplotlib figure and axes objects

        Note
        ----
        Plotting all points in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `plot_lines_sample_n_alt_axes` is recommended.

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        # Scatter x, y, z, [color]

        x = self._point_data[:, 1]
        y = self._point_data[:, 2]
        z = self._point_data[:, 3]

        color = self._point_data[:, -1]

        cmap = plt.cm.magma
        color_array = cmap(color)

        ax.scatter(z,x,y,c=color_array[0])

        return fig, ax


    def plot_points_sample_n(self, n, ax=None):
        '''Plot points from sample `n` using matplotlib

        Given a **mpl_toolkits.mplot3d.Axes3D** axis, plots all points
        from sample number `n`.

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.
        n : int
            The number of the sample to be plotted.

        Returns
        -------

        fig, ax : matplotlib figure and axes objects

        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        # Scatter x, y, z, [color]

        sample = self.sample_n(n)

        x = sample[:, 1]
        y = sample[:, 2]
        z = sample[:, 3]

        color = sample[:, -1]

        cmap = plt.cm.magma
        color_array = cmap(color)

        ax.scatter(z,x,y,c=color_array[0])

        return fig, ax


    def plot_points_sample_n_alt_axes(self, n, ax=None):
        '''Plot points from sample `n` using matplotlib on PEPT-style axes

        Given a **mpl_toolkits.mplot3d.Axes3D** axis, plots all points from
        sample number sampleN on the PEPT-style coordinates convention:
        **x** is *parallel and horizontal* to the screens, **y** is
        *parallel and vertical* to the screens, **z** is *perpendicular*
        to the screens. The mapping relative to the Cartesian coordinates
        would then be: (x, y, z) -> (z, x, y)

        Parameters
        ----------
        ax : mpl_toolkits.mplot3D.Axes3D object
            The 3D matplotlib-based axis for plotting.
        n : int
            The number of the sample to be plotted.

        Returns
        -------

        fig, ax : matplotlib figure and axes objects
        '''

        if ax == None:
            fig = plt.figure()
            ax  = fig.add_subplot(111, projection='3d')
        else:
            fig = plt.gcf()

        # Scatter x, y, z, [color]

        sample = self.sample_n(n)

        x = sample[:, 1]
        y = sample[:, 2]
        z = sample[:, 3]

        color = sample[:, -1]

        cmap = plt.cm.magma
        color_array = cmap(color)

        ax.scatter(z,x,y,c=color_array[0])

        return fig, ax


    def all_points_trace(self, size = 2, color = None):
        '''Get a Plotly trace of all points.

        Creates a `plotly.graph_objects.Scatter3d` object. Can
        then be passed to the `plotly.graph_objects.figure.add_trace`
        function or a `PlotlyGrapher` instance using the `add_trace` method.

        Returns
        -------
        plotly.graph_objects.Scatter3d
            A `plotly.graph_objects.Scatter3d` trace of all points.

        Note
        ----
        Plotting all points in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `points_sample_n_traces` is recommended.

        '''

        trace = go.Scatter3d(
            x = self._point_data[:, 1],
            y = self._point_data[:, 2],
            z = self._point_data[:, 3],
            mode = 'markers',
            marker = dict(
                size = size,
                color = color,
                opacity = 0.8
            )
        )

        return trace


    def all_points_trace_colorbar(self, size = 2, colorbar_title = None):
        '''Get a Plotly trace of all points, colour-coding the last column of `point_data`.

        Creates a `plotly.graph_objects.Scatter3d` object. Can
        then be passed to the `plotly.graph_objects.figure.add_trace`
        function or a `PlotlyGrapher` instance using the `add_trace` method.

        Returns
        -------
        plotly.graph_objects.Scatter3d
            A `plotly.graph_objects.Scatter3d` trace of all points.

        Note
        ----
        Plotting all points in the case of large LoR arrays is *very*
        computationally intensive. For large arrays (> 10000), plotting
        individual samples using `points_sample_n_traces` is recommended.

        '''

        if colorbar_title != None:
            colorbar = dict(title = colorbar_title)
        else:
            colorbar = dict()

        trace = go.Scatter3d(
            x = self._point_data[:, 1],
            y = self._point_data[:, 2],
            z = self._point_data[:, 3],
            mode = 'markers',
            marker = dict(
                size = size,
                color = self._point_data[:, -1],
                colorscale = 'Magma',
                colorbar = colorbar,
                opacity = 0.8
            )
        )

        return trace


    def points_sample_n_trace(self, n, size = 2, color = None):
        '''Get a Plotly trace for all points in sample `n`.

        Returns a `plotly.graph_objects.Scatter3d` trace containing all points
        included in sample number `n`.
        Can then be passed to the `plotly.graph_objects.figure.add_trace`
        function or a `PlotlyGrapher` instance using the `add_trace` method.

        Parameters
        ----------
        n : int
            The number of the sample to be plotted.

        Returns
        -------
        plotly.graph_object.Scatter3d
            A `plotly.graph_objects.Scatter3d` trace of all points in sample `n`.

        '''

        sample = self.sample_n(n)
        trace = go.Scatter3d(
            x = sample[:, 1],
            y = sample[:, 2],
            z = sample[:, 3],
            mode = 'markers',
            marker = dict(
                size = size,
                color = color,
                opacity = 0.8
            )
        )

        return trace


    def points_sample_n_trace_colorbar(self, n, size = 2, colorbar_title = None):
        '''Get a Plotly trace for all points in sample `n`, colour-coding the last column.

        Returns a `plotly.graph_objects.Scatter3d` trace containing all points
        included in sample number `n`.
        Can then be passed to the `plotly.graph_objects.figure.add_trace`
        function or a `PlotlyGrapher` instance using the `add_trace` method.

        Parameters
        ----------
        n : int
            The number of the sample to be plotted.

        Returns
        -------
        plotly.graph_object.Scatter3d
            A `plotly.graph_objects.Scatter3d` trace of all points in sample `n`.

        '''

        if colorbar_title != None:
            colorbar = dict(title = colorbar_title)
        else:
            colorbar = dict()

        sample = self.sample_n(n)
        trace = go.Scatter3d(
            x = sample[:, 1],
            y = sample[:, 2],
            z = sample[:, 3],
            mode = 'markers',
            marker = dict(
                size = size,
                color = sample[:, -1],
                colorscale = 'Magma',
                colorbar = colorbar,
                opacity = 0.8
            )
        )

        return trace


    def __len__(self):
        # Defined so that len(class_instance) returns the number of samples.

        return self.number_of_samples


    def __str__(self):
        # Shown when calling print(class)
        docstr = ""

        docstr += "sample_size = {}\n".format(self._sample_size)
        docstr += "overlap =     {}\n\n".format(self._overlap)
        docstr += "point_data = \n"
        docstr += self._point_data.__str__()

        return docstr


    def __repr__(self):
        # Shown when writing the class on a REPR

        docstr = "Class instance that inherits from `pept.PointData`.\n\n" + self.__str__() + "\n\n"
        docstr += "Particular cases:\n"
        docstr += " > If sample_size == 0, all point_data is returned as one single sample.\n"
        docstr += " > If overlap >= sample_size, an error is raised.\n"
        docstr += " > If overlap < 0, points are skipped between samples.\n"

        return docstr


    def __getitem__(self, key):
        # Defined so that samples can be accessed as class_instance[0]

        if self.number_of_samples == 0:
            raise IndexError("Tried to access sample {} (indexed from 0), when there are {} samples".format(key, self.number_of_samples))

        if key >= self.number_of_samples:
            raise IndexError("Tried to access sample {} (indexed from 0), when there are {} samples".format(key, self.number_of_samples))


        while key < 0:
            key += self.number_of_samples

        return self.sample_n(key + 1)


    def __iter__(self):
        # Defined so the class can be iterated as `for sample in class_instance: ...`
        return self


    def __next__(self):
        # sample_size = 0 => return all data
        if self._sample_size == 0:
            self._sample_size = -1
            return self._point_data
        # Use -1 as a flag
        if self._sample_size == -1:
            self._sample_size = 0
            raise StopIteration

        # sample_size > 0 => return slices
        if self._index != 0:
            self._index = self._index + self._sample_size - self.overlap
        else:
            self._index = self._index + self.sample_size


        if self._index > self.number_of_points:
            self._index = 0
            raise StopIteration

        return self._point_data[(self._index - self._sample_size):self._index]




